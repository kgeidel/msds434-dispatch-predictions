# Python imports
import os
import datetime as dt
from io import StringIO
from itertools import product

# Django imports
import boto3.session
from django.utils import timezone
from django.db import models

# 3rd party imports
import pandas as pd
import boto3;
import sagemaker;
from tqdm import tqdm

# Intraproject imports
from django.conf import settings
from calls.models import Incident, DISP


class Forecast(models.Model):
    ''' An instance of the class represents forecasted call volume for a specfic date range '''

    class Settings:
        ml_auto_experiment_name = 'dispatch-predictions-automl'
        sagemaker_role_arn = os.getenv('SAGEMAKER_ROLE_ARN')
        sagemaker_kms_arn = os.getenv('SAGEMAKER_KMS_ARN')
        s3_bucket_name = 'dispatch-predictions'
        data_file_name = 'incidents_per_day.csv'
        target_attr = 'incident_count'

    dtg_predicted = models.DateTimeField(auto_now_add=True)
    predictions_json = models.JSONField(null=True, blank=True)

    @staticmethod
    def get_sagemaker_df(date_start=None, date_end=None):
        fkwargs = {}
        # add date filters if supplied
        if date_start is not None:
            assert isinstance(date_start, dt.date), f"If date_start is supplied, it must be type datetime.date, not {type(date_start)}"
            fkwargs.update({'dtg_alarm__date__gte': date_start})
        if date_end is not None:
            assert isinstance(date_end, dt.date), f"If date_end is supplied, it must be type datetime.date, not {type(date_end)}"
            fkwargs.update({'dtg_alarm__date__lte': date_end})
        # get df from base qs
        df = pd.DataFrame(Incident.objects.filter(**fkwargs).values('dtg_alarm'))
        # Aggregate calls into a count by date
        df = df.groupby(df['dtg_alarm'].dt.date).count()
        # fill in missing dates with zero counts
        all_dates = pd.date_range(df.index.min(), date_end or timezone.now().date())
        df = df.reindex(all_dates).fillna(0)
        df = df.astype(int)
        df = df.reset_index()
        df = df[['dtg_alarm', 'index']]
        df.columns = ['incident_count', 'date']
        return df

    @classmethod
    def get_boto3_session(cls):
        if not getattr(cls, '_boto3_session', None):
            cls._boto3_session = boto3.Session()
        return cls._boto3_session        

    @classmethod
    def get_sagemaker_client(cls):
        if not getattr(cls, '_sagemaker_client', None):
            cls._sagemaker_client = boto3.client('sagemaker')
        return cls._sagemaker_client   

    @classmethod
    def get_s3_resource(cls):
        if not getattr(cls, '_s3_resource', None):
            cls._s3_resource = cls.get_boto3_session().resource('s3')
        return cls._s3_resource   

    @classmethod
    def update_s3_data_source(cls):
        df = Forecast.get_sagemaker_df()
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, header=True)
        cls.get_s3_resource().Object(cls.Settings.s3_bucket_name, cls.Settings.data_file_name).put(Body=csv_buffer.getvalue())

    @classmethod
    def get_best_candidate_model_name(cls):
        return cls.get_sagemaker_client().list_models().get('Models')[0].get('ModelName')

    @classmethod
    def create_auto_ml_job(cls):
        response = cls.get_sagemaker_client().create_auto_ml_job(
            AutoMLJobName = cls.Settings.ml_auto_experiment_name,
            InputDataConfig = [
                {
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': f's3://{cls.Settings.s3_bucket_name}/{cls.Settings.data_file_name}'
                        }
                    },
                    'TargetAttributeName': cls.Settings.target_attr,
                    'ChannelType': 'training'
                },
            ],
            OutputDataConfig={
                'S3OutputPath': f's3://{cls.Settings.s3_bucket_name}/output'
            },
            RoleArn=os.getenv('SAGEMAKER_ROLE_ARN')
        )
        return response

    @classmethod
    def create_forecast_model(cls):
        automl = sagemaker.AutoML.attach(auto_ml_job_name=cls.Settings.ml_auto_experiment_name)
        # Describe and recreate the best trained model
        best_candidate = automl.describe_auto_ml_job()['BestCandidate']
        best_candidate_name = best_candidate['CandidateName']
        response = automl.create_model(
            name=best_candidate_name, 
            candidate=best_candidate, 
            inference_response_keys=['predicted_label']
        )
        return response
    
    @classmethod
    def deploy_forecast_model(cls):
        cls.get_sagemaker_client().create_endpoint_config(
            EndpointConfigName=f'{cls.Settings.ml_auto_experiment_name}-config',
            ProductionVariants=[{
                'InstanceType': 'ml.m4.xlarge',
                'InitialInstanceCount': 1,
                'ModelName': cls.get_best_candidate_model_name(),
                'VariantName': 'AllTraffic'
            }]
        )
        # deploy the model by creating the endpoint
        create_endpoint_response = cls.get_sagemaker_client().create_endpoint(
            EndpointName=f'{cls.Settings.ml_auto_experiment_name}-endpoint',
            EndpointConfigName=f'{cls.Settings.ml_auto_experiment_name}-config'
        )
        return create_endpoint_response['EndpointArn']
    
    @classmethod
    def make_predictions(cls):
        endpoint_name = cls.get_sagemaker_client().list_endpoints()['Endpoints'][0]['EndpointName']
        prediction_client = boto3.client('runtime.sagemaker')
        next_7_days = pd.date_range(start=pd.Timestamp.today(), periods=7, freq='D')
        dates_df = pd.DataFrame({'incident_date': next_7_days})
        dates = dates_df.to_csv(header=False, index=False)
        response = prediction_client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Body=dates
        )
        body = response['Body']
        from sagemaker.amazon.common import RecordDeserializer
        def recordio_protobuf_deserialize(data, content_type):
            rec_des = RecordDeserializer()
            return rec_des.deserialize(data, content_type)

        output = recordio_protobuf_deserialize(body, str)
        values = [o.label['values'].float32_tensor.values[0] for o in output]
        values = [int(x) if x >= 0 else 0 for x in values]
        df = pd.DataFrame(zip(next_7_days, values), columns=['date', 'prediction'])
        df['date'] = df['date'].apply(lambda x: str(x)[:10])
        df.set_index('date')
        predictions_json = df.to_json(orient='records')
        Forecast.objects.create(predictions_json=predictions_json)
    
    @classmethod
    def clean_up_sagemaker_resources(cls, delete_experiments=False):
        client = cls.get_sagemaker_client()
        # Delete Models
        for model in client.list_models().get('Models'):
            client.delete_model(ModelName=model.get('ModelName'))
        # Endpoints
        for record in client.list_endpoints().get('Endpoints'):
            client.delete_endpoint(EndpointName=record.get('EndpointName'))
        # Endpoint configs  
        for record in client.list_endpoint_configs().get('EndpointConfigs'):
            client.delete_endpoint_config(EndpointConfigName=record.get('EndpointConfigName'))
        if delete_experiments:
            # auto_ml experiments
            trials = [r.get('TrialName') for r in client.list_trials().get('TrialSummaries')]
            components = [r.get('TrialComponentName') for r in client.list_trial_components().get('TrialComponentSummaries')]
            # disassociate all components from all trials
            print("disassociating components from trials...")
            for component, trial in tqdm(product(components, trials)):
                client.disassociate_trial_component(TrialComponentName=component, TrialName=trial)
            # should be able to delete them now
            print("deleting components...")
            for component in tqdm(components):
                client.delete_trial_component(TrialComponentName=component)
            print("deleting trials...")
            for trial in tqdm(trials):
                client.delete_trial(TrialName=trial)
            # Experiments should be OK to delete now...
            print("deleting auto_ml_jobs...")
            for experiment in tqdm(client.list_experiments().get('ExperimentSummaries')):
                print(experiment)
                client.delete_experiment(ExperimentName=experiment.get('ExperimentName'))
