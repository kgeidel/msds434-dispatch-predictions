# MSDS 434 Dispatch Predictions

<div align=center>

DISPATCH PREDICTIONS: <br>MACHINE LEARNING ON EMERGENCY SERVICE CALL VOLUME  
</div>
<br><br>

<div align=center>

Kevin Geidel <br>
MSDS 434: Data Science & Cloud Computing<br>
Northwestern University<br>
March 16, 2025
<br>
</div>
<br>
</p>
<hr>

## Overview

I am in section 55 (Winter '25.) This is my term project. <br>

The final reflection paper can be found <img src="https://upload.wikimedia.org/wikipedia/commons/6/6c/PDF_icon.svg" height="20" width="20"><a href="https://drive.google.com/file/d/1tsuD7azuyu8nWILJfropiofXHYQahV10/view?usp=sharing" target="_blank">here.</a>

You can access the web app at <a href="http://msds434.ddns.net:8000" target="_blank">http://msds434.ddns.net:8000</a><br>
If the page does not load I may have stopped the EC2 to limit costs. [Reach out to me](mailto:kevingeidel2024@u.northwestern.edu) and I can start it back up for you!

Please visit my <img src="https://kstatic.googleusercontent.com/files/d57b24106c34c7e50ef3d98423b94ddaf35ad2da73a9b9d4d12f52dbb9dd4c08c2957f6255ab8690d5ef0b32cff8287e09577d05e479d263e872160c4c9e8363" height="20" width="20">[Google Drive Folder](https://drive.google.com/drive/folders/1so_fM2HcdTYzCYSuwtdbxBeXtx1CPN8J?usp=sharing) for the project update videos.

- [User documentation](#user-documentation)
- [Step 1: Identify the problem](#the-problem)
- [Step 2: Identify the data set](#the-data-set)
- [Step 3: Construct a functional specification](#functional-specification)
- [Step 4: Data ingest](#data-ingest)
- [Step 5: ML demonstration](#exploring-ml-options)
- [Step 6: ML deployment](#ml-deployment)
- [Step 7: Microservice development](#microservice-development)
- [Step 8: Microservice deployment](#microservice-deployment)
- [Step 9: Performance monitoring](#resource-and-performance-monitoring)
- [Step 10: Production environment](#production-environment)

## User documentation

* [Navigation](#navigation)
* [API access](#api-access) 

#### Navigation

Each view in the site contains a nav bar at the top of the page. The main options are as follows:

| Item | Description |
| ---- | :---------- |
| A | The **calls** app contains lookups for incidents and call dispositions.  |
| B | The **forecast** app contains the ML predictions in table and graphical forms. |
| C | The **API browser** is a GUI tool for interacting with the REST API. |
| D | The **admin** panel is for managing users, groups and api tokens. |
| E | The **readme** is this document. |
| F | The **monitor** tool is the Prometheus GUI. |

![nav bar](docs/imgs/home_page.png)

#### API access

Obtain a web API token from the [Admin panel](http://msds434.ddns.net:8000/admin)- all requests (GET and POST) to the **dispatch-predictions** API require an authorization header of the form `Token <your-web-api-token>`. Any method for generating web requests will suffice. Here is an example using Python's `requests` package. 

```python
import requests, json
from pprint import pprint
 
api_token = 'YOUR API TOKEN'
 
# Query the first page of incidents 
r = requests.get(
    'http://msds434.ddns.net:8000/api/calls/',
    headers = {
        "Authorization": f'Token {api_token}'
    }
)
 
# display the json response
pprint(json.loads(r.content))
```

The [API browser](http://msds434.ddns.net:8000/api/) is the best way to explore the options for the API.

## The problem

Low staffing in emergency services is problematic for many organizations; particularly volunteer fire departments. The issue is compounded during high call volume times (i.e. Winter storm events.) There are a number of strategies for alleviating the complications surrounding personnel shortages including duty crews and/or key members [i.e. chauffeurs] taking fly cars home with them. In paid departments there are also callbacks and overtime. The decision to deploy such tactics is largely informed by experience (and external information such as weather forecasts.)

**dispatch-predictions** aims to use *Machine Learning (ML)* to model the demand for fire & rescue services (calls/incidents) and use the model to predict future call volume. Specifically:

* When is the next call likely to occur?
* How many calls are expected in the next 1 hour? 24 hours? 48 hours? week?, etc.
* What factors influence the likely probability of a call occurring?
* Would the ML model be more reliable if fed raw time-series historical data or if it is used to solve a preformulated decision analytics problem (i.e a Queue problem?)
* What ML algorithms are best suited for this task?

## The data set

* Data consists of incident call logs from the [Hughsonville Fire Department](https://www.hfd45.org).
* Current state of the data is an xls export (1998-01-02 to 2025-01-14.)
* I am working on programmatic access to the Microsoft SQL Server that hosts it.
* Remainder of initial analysis performed in the form of *Exploratory Data Analysis (EDA)*:

```python
# MSDS 434 - Section 55
# Winter '25
# dispatch-predictions - EDA

# Kevin Geidel

from matplotlib import pyplot as plt
import pandas as pd
pd.set_option('display.max_rows', 500)
```
```python
file_path = 'data/2025_01_14_hfd_incident_log.xls'

df = pd.read_excel(file_path, parse_dates=[['Date', 'Alarm']])

df.head()  # Raw data frame
```
<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Date_Alarm</th>
      <th>FDID</th>
      <th>Incident#</th>
      <th>Num</th>
      <th>Address</th>
      <th>Suite</th>
      <th>Zip</th>
      <th>Type</th>
      <th>Lgth</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01/02/2000 13:41</td>
      <td>14013.0</td>
      <td>2000-000001</td>
      <td>10</td>
      <td>BARBARA LA.</td>
      <td></td>
      <td>12590</td>
      <td>Natural vegetation fire</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>01/04/2000 12:30</td>
      <td>14013.0</td>
      <td>2000-000002</td>
      <td>2015</td>
      <td>ROUTE 9 - UNIT 16</td>
      <td></td>
      <td>12590</td>
      <td>Emergency medical service (EMS) Incident</td>
      <td>0.5</td>
    </tr>
    <tr>
      <th>2</th>
      <td>01/04/2000 12:36</td>
      <td>14013.0</td>
      <td>2000-000003</td>
      <td>52</td>
      <td>OSBORNE HILL RD.</td>
      <td></td>
      <td>12590</td>
      <td>Emergency medical service (EMS) Incident</td>
      <td>0.7</td>
    </tr>
    <tr>
      <th>3</th>
      <td>01/05/2000 22:13</td>
      <td>14013.0</td>
      <td>2000-000004</td>
      <td>NaN</td>
      <td>NEW HAMBURG RD. @ WHEELER</td>
      <td></td>
      <td>12590</td>
      <td>Service call, other</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>01/07/2000 22:34</td>
      <td>14013.0</td>
      <td>2000-000005</td>
      <td>206</td>
      <td>OLD HOPEWELL RD.</td>
      <td></td>
      <td>12590</td>
      <td>Good intent call, other</td>
      <td>0.3</td>
    </tr>
  </tbody>
</table>
</div>

```python
# stats on the raw dataframe
df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 16172 entries, 0 to 16171
    Data columns (total 9 columns):
     #   Column      Non-Null Count  Dtype  
    ---  ------      --------------  -----  
     0   Date_Alarm  16172 non-null  object 
     1   FDID        15483 non-null  float64
     2   Incident#   15483 non-null  object 
     3   Num         13410 non-null  object 
     4   Address     15482 non-null  object 
     5   Suite       15437 non-null  object 
     6   Zip         15468 non-null  object 
     7   Type        16148 non-null  object 
     8   Lgth        15483 non-null  float64
    dtypes: float64(2), object(7)
    memory usage: 1.1+ MB
```python
# 689 records (16172 - 15483) don't have dates, incident #s or times.
# This looks like a issue with exporting certain call types 
# (maybe there was a newline char in the text?)
# drop records w/o dates

df = df.dropna(subset=['Incident#'])

# Coax cols into proper dtypes
df['FDID'] = df['FDID'].astype(str)
df['Date_Alarm'] = df['Date_Alarm'].astype('datetime64[s]')

# Repair the broken Type
broken_type = 'Unintentional system/detector operation (no '
df.loc[df['Type']==broken_type, 'Type'] = broken_type + 'fire)'

# re-check breakdown of rows/cols
df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    Index: 15483 entries, 0 to 16171
    Data columns (total 9 columns):
     #   Column      Non-Null Count  Dtype        
    ---  ------      --------------  -----        
     0   Date_Alarm  15483 non-null  datetime64[s]
     1   FDID        15483 non-null  object       
     2   Incident#   15483 non-null  object       
     3   Num         13410 non-null  object       
     4   Address     15482 non-null  object       
     5   Suite       15437 non-null  object       
     6   Zip         15468 non-null  object       
     7   Type        15459 non-null  object       
     8   Lgth        15483 non-null  float64      
    dtypes: datetime64[s](1), float64(1), object(7)
    memory usage: 1.2+ MB



```python
# Visualize the data

# Group by date
calls_per_day = df['Date_Alarm'].groupby([df['Date_Alarm'].dt.date]).count()

calls_per_day.plot.line()
plt.title("Calls per day")
plt.ylabel("Number of incidents")
plt.show()
```    
![png](docs/imgs/EDA_4_0.png)
```python
# Some descriptive statistics for daily call distribution
calls_per_day.describe()
```
    count    7471.000000
    mean        2.072413
    std         1.393897
    min         1.000000
    25%         1.000000
    50%         2.000000
    75%         3.000000
    max        47.000000
    Name: Date_Alarm, dtype: float64
```python
# view the distribution of calls per day

plt.boxplot(calls_per_day, orientation='horizontal');
plt.title("Distribution of daily calls")
plt.yticks([]);
``` 
![png](docs/imgs/EDA_6_0.png)
```python
# Try again by week

calls_per_week = df[['Date_Alarm', 'Incident#']].groupby([pd.Grouper(key='Date_Alarm', freq='W')]).count()

calls_per_week.plot.line()
plt.title("Calls per week")
plt.ylabel("Number of incidents")
plt.show()
```
![png](docs/imgs/EDA_7_0.png)
```python
# Some descriptive statistics for weekly call distribution
calls_per_week.describe()
```
<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Incident#</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1412.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>10.965297</td>
    </tr>
    <tr>
      <th>std</th>
      <td>4.714327</td>
    </tr>
    <tr>
      <th>min</th>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>8.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>11.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>14.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>61.000000</td>
    </tr>
  </tbody>
</table>
</div>

```python
plt.boxplot(calls_per_week, orientation='horizontal');
plt.title("Distribution of weekly calls")
plt.yticks([]);
```
![png](docs/imgs/EDA_9_0.png)

<hr>

## Functional specification

#### Project overview

  &nbsp;&nbsp;&nbsp;&nbsp;**dispatch-predictions** aims to forecast the occurrence of emergency incidents for a volunteer fire department. The primary objective is to let Chief officers and line officers respond proactively to upcoming high call volume times.

#### User roles & capabilities

  &nbsp;&nbsp;&nbsp;&nbsp;There is one class of users: firematic officers. They will have access to the forecasts, descriptive metrics and status of the model (i.e. feature importance, last update, number of records, etc.)

#### Core functionality

  &nbsp;&nbsp;&nbsp;&nbsp;**Data collation** will occur via GoLang pipelines consisting of HTTP API streams from a client portion with access to the department's incident log and a server portion that handles data cleaning, feature engineering and the analytics mirror database. 

  &nbsp;&nbsp;&nbsp;&nbsp;**Forecasting** will be accomplished via time series regression using Python's SciKitLearn. Pandas will be used for data manipulation throughout.

  &nbsp;&nbsp;&nbsp;&nbsp;**Reporting** will provide both a web-based UI and Restful API.

#### Technical requirements
   
  * Cloud based virtual machine: AWS EC2 t2.micro running Ubuntu 24.04
  * RDMS: AWS Aurora running PostgreSQL16
  * Web application: Django framework with both web browser GUI and Rest API
  * ML pipeline: Transformations, cleaning and models via SciKitLearn
  * Data stream generator: GoLang service on FD workstation

#### Non-functional requirements

  * Non-public information should not be made available without user authentication. 
  * Maximum up time will ensure quality forecasts and actionable insights.
  * Straightforward UI for non-technical users.


#### Error reporting & monitoring

  &nbsp;&nbsp;&nbsp;&nbsp;**System logs** will be maintained with OS, application and network warnings, errors and information. These are for developers to monitor the status of the web app and address any issues. Email **alerts** will be used to notify developers when errors are logged.

  &nbsp;&nbsp;&nbsp;&nbsp;The Django messages framework will be utilized to generate and display notifications to users on the web app's GUI. These will include warnings, errors and information.

#### Architecture & design
 
 &nbsp;&nbsp;&nbsp;&nbsp;Below is a flowchart to illustrate how the system works and how users navigate through it. A description of how each element interacts with one another follows.

  ![png](docs/imgs/architecture.png)

  **(A):** The stream generator is a custom GoLang package that retrieves call log data from the fire department database by issuing queries. The database returns results to the generator.

  **(B):** The generator will need to query the API with a GET request in order to determine which records are new and must be sent. The API will respond with the latest call in the database. The generator service will then issue a POST request to the API with the latest incidents.

  **(C):** The API must write new incidents into the database. The API will also query the database for call meta data (i.e. most recent call.) Finally, the API can also be used for programmatic access to the raw data, ML model meta data and forecasts themselves.

  **(D):** The web application will be used to construct the views needed for the API to perform its duties. These include providing serializers, view sets and filters.

  **(E):** The web application will query the database for raw data, ML forecasts and system meta data. The database will return query results for display in tables, reports and alerts.

  **(F):** The web application will trigger ML methods: cleaning, transformations, modeling, etc. The web application will also provide the records used in training, testing and prediction. The pipeline returns prediction results and meta data about the forecasts (i.e. feature importance, confidence intervals, etc.)
  
  **(G):** The web application provides views that take requests and return the HTTP responses that constitute the GUI.

  **(H):** Non-technical users and non-developer stake holders (firematic officers) will use the GUI to interact with the forecasts. This will occur in tables, reports and visualizations. 

  **(I):** Developers and other technical users can use the GUI as well.

  **(J):** Technical users will be able to use HTTP web requests to query the API directly for whatever their permissions allow (raw data, meta data, forecast data, etc.)

#### Deployment

* **dispatch-predictions** will be a containerized application (via **docker**) and deployed from a cloud based virtual machine. AWS will be utilized for its IaaS products. The developer will provision, manage, monitor and maintain the servers hosting the various components of the web app.

* There are several distinct advantages to this approach when compared to other deployment tactics (such as using a PaaS framework like Elastic Beanstalk from AWS.) 
  * Only provision what you need. You are the system admin!
  * There are less moving parts when compared to full featured app engines that try to do it all.  
  * Tighter control over security. PaaS products typically use shared VPCs, security rules, roles/permissions, etc. 
  * Less dependence on a particular vendor. There are innumerable ways to get servers on the web in an affordable manner and our containerized application will run on essentially all of them. 

* As development proceeds there will be deliberate efforts to try and mitigate the disadvantages to this approach (as compared to PaaS.)
  * There is more for developers to manage. They are full stack and this means more user stories, more technologies to learn, more irons in the fire in general.
  * As a corollary to the point above, we are not as agile as we would of been using PaaS for deployment. We must provision our own resources, maintain our own infrastructure and maintain our own CI/CD work flows.
  * The above points can lead to higher barrier to entry for teams with out the full stack skill set or resource capacity. 

#### Example UI
  
  &nbsp;&nbsp;&nbsp;&nbsp;Users may see a main dashboard screen similar to the one shown below. This mock up captures the primary MVP objectives but does not include many stretch features that may or may not be incorporated. As development proceeds there will emerge a clearer picture of what the delivered application will be able to do and look like.

  ![png](docs/imgs/UI_mockup.png)


#### Version control, review & documentation
  
  &nbsp;&nbsp;&nbsp;&nbsp;The project, including this technical specification, is stored in a **git** repository. The upstream remote for the repo can be found at [https://github.com/kgeidel/msds434-dispatch-predictions](https://github.com/kgeidel/msds434-dispatch-predictions). Additional documentation can be found in the README, `docs` directory, `man` directory and throughout the code base in the form of doc strings and comments. Stakeholders are encouraged to review this documentation and respond with their approval or concerns to the developer.

## Data ingest

There are two vectors for loading incident records into the database. The first is [a bulk upload](#bulk-upload-of-redalertnmx-exports) for back populating purposes. The second is the primary way in which the database receives new records and involves [sending records through a web-based RESTful API](#stream-processing-of-new-incident-records).

#### Bulk upload of RedAlertNMX exports

In the Django project directory (`dispatch-predictions-app`) is a Jupyter notebook with a script that can load records from an excel spreadsheet (xls format.) This logic could easily be moved to a static method on the **Incident** model but this process it only for populating a fresh database with historical records. It will not be used once the database is populated and the entirety of the architecture is deployed.

The spreadsheet comes from the client application used by the firehouse- *RedAlertNMX*. There are about 15,400 records so they easily fit in a single spreadsheet. There is some column cleaning and preprocessing that must take place in the script before the records are fit for consumption.

Pandas is used to load the data from the spreadsheet and perform the preprocessing steps. Once the data is cleaned we iterate through the records of the dataframe and use the Django ORM to create the instances.

```python
# Python imports
import os

# Django imports
from django.utils import timezone
import datetime as dt

# 3rd party imports
from tqdm import tqdm
import pandas as pd
pd.set_option('display.max_rows', 500)

# Intraproject imports
import django_init
from django.conf import settings
from calls.models import Incident, DISP

# load into pandas dataframe with proper cleaning & transforming
input_path = os.path.join(
    settings.BASE_DIR.parent, 
    'data', '2025_01_14_hfd_incident_log.xls',
)

df = pd.read_excel(input_path, parse_dates=[['Date', 'Alarm']])
df = df.dropna(subset=['Incident#'])
df['FDID'] = df['FDID'].astype(str)
df['Date_Alarm'] = df['Date_Alarm'].astype('datetime64[s]')
broken_type = 'Unintentional system/detector operation (no '
df.loc[df['Type']==broken_type, 'Type'] = broken_type + 'fire)'

# load into database

for index, record in tqdm(df.iterrows()):
  Incident.objects.get_or_create(
      num = str(record['Incident#']).strip(),
      dtg_alarm = record['Date_Alarm'].to_pydatetime().astimezone(settings.TIME_ZONE_OBJ),
      defaults = dict(
          fd_id = str(record['FDID']).strip('.0'),
          street_number = str(record['Num']).strip() if pd.notna(record['Num']) else None,
          route = str(record['Address']).strip() if pd.notna(record['Address']) else None,
          suite = str(record['Suite']).strip() if pd.notna(record['Suite']) else None,
          postal_code = str(record['Zip']).replace('-', '').strip()[:5] if pd.notna(record['Zip']) else None,
          disp = DISP.objects.get_or_create(type_str=str(record['Type']).strip())[0] if pd.notna(record['Type']) else None,
          duration = record['Lgth'] if pd.notna(record['Lgth']) else None,
      )
)
```
#### Stream processing of new incident records

Once the database is caught up with the system of record (the firehouse's MS SQL Server) we only need to process new calls as they occur. 


>In the final state this will be accomplished by a Go application that runs on a workstation with access to the system of record. While this component is still being developed, I have completed the REST API that will accept the list of new calls via POST web requests. This component will be demonstrated below.


Here is a python example of what the Go application would need to replicate to add records to the database (this could also be accomplished with curl or the browsable API site.)

```python
import requests, json, os
from pprint import pprint

token = os.getenv('WEB_APP_API_TOKEN')

data = [
    {'num': 'FOO', 'dtg_alarm': "1998-08-28T13:41:00-05:00"},
    {'num': 'BAR', 'dtg_alarm': "2525-01-02T13:41:00-05:00"},
]

requests.post(
    'http://localhost:8000/api/calls/bulk_update_or_create/', 
    headers={'Authorization': f'Token {token}'}, json=data
)
```

This would add two calls, one with call number "FOO" and the other "BAR" to the database. This process is demonstrated in the Week 4 project update video.

## Exploring ML options

Several methods of deploying Machine Learning (ML) models were evaluated. The benchmark cloud platform services were compared to is a locally hosted SciKitLearn model and pipeline. The first cloud based method involves an ETL from the production database (RDS) into Red Shift and using Auto ML's Forecast model. The second invoked Sage maker studio and the third uses the Sage maker Python SDK for programmatic control of the prerequisite AWS resources.

![AutoML screenshot](docs/imgs/automl.png)

Sake maker SDK was selected to deploy the project's ML component moving forward. AWS Forecast took a very long time to train and predict and was quite expensive, even for the minimal experiment that was run. The benefits of Sage maker SDK, used in conjunction with boto3, is the ability to develop processing pipelines right in the web application. 

## ML deployment

The Sage maker SDK client and resource API object were used to build classmethods for the Forecast model. These methods constitute the ML pipeline that dispatch-predictions must run (likely weekly.) Programmatic Time Series forecasting is extremely problematic with AWS cloud products. Sage maker and AutoML require transformations to approximate time series forecasting. The AWS Forecast models are no longer available programmatically to new users. Because of these factors the auto_ml_experiment methods from the sage maker SDK are likely to be replaced by a similar SciKitLearn pipeline. This will allow for native time series forecasting, avoid expensive AutoML experiments and simplify the AWS resources needed. This refactor would aim to mimic the sage maker process already developed and demonstrated.

```python
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
```


## Microservice development

A GoLang microservice was developed for dispatch-predictions. The job of this service is to obtain filter parameters from the web app, use the returned arguments to query new incidents from the firehouse incident system of record and finally post the new incidents to the web app's API for processing. 

The microservice uses the `github.com/microsoft/go-mssqldb` package to query the MS SQL server that functions as the firehouse's system of record for emergency calls.

![M$ SQL QSTR](docs/imgs/microservice_qstr.png)

The returned results are mapped into a slice of Go structs. JSON field attribute names are included for marshaling to POST request payloads.

```go
// A struct to contain an individual incident record
type Incident struct {
	Num           string `json:"num"`
	Dtg_alarm     string `json:"dtg_alarm"`
	Fd_id         string `json:"fd_id"`
	Street_number string `json:"street_number"`
	Route         string `json:"route"`
	Suite         string `json:"suite"`
	Postal_code   string `json:"postal_code"`
	Call_duration string `json:"duration"`
	Type_str      string `json:"type_str"`
}
```

## Microservice deployment

The Go microservice developed to push new incidents to the RDS was deployed as a Docker container. A `docker-compose.yml` is used to describe the service. It references a Dockerfile that contains instructions for building dependencies and deploying the application. In the module 8 project update video I discuss the changes that would make sense if using this method in production (namely, moving the scheduling logic to main.go, allowing the service to run in the background without the need of a task scheduler.) That update also includes discussion about implementing a publisher/subscriber stream processing model. Instead of having the microservice communicate directly with the web app we could decouple the processes and make the uptake of new incident records asynchronous. The microservice could push new calls to a message queue (a la AWS's Simple Queue Service, SQS.) The web app could process them at its leisure. Pros and cons were discussed. First and foremost, this introduces new infrastructure and makes the overall architecture more complicated. An advantage would be calls could be entered to the queue even if the web app is down and they would be there waiting when the app came back online.

## Resource and performance monitoring

The `monitoring` directory at project level contains docker-compose configurations to integrate Prometheus and Grafana into dispatch-predictions. To launch the monitoring spin up the services defined in the docker-compose.

```shell
# enter the monitoring directory from project root
cd monitoring

# launch the services in daemon mode
docker compose up -d
```

To view the Prometheus metrics visit the EC2's IP address at port `9090`. In order to have Django generate the metrics install the django-prometheus package `pip install django-prometheus`. You must register the package in Django settings and install the middleware at the beginning and end of any other middleware in use.

```python
# In settings.py....

INSTALLED_APPS = [
  # all the other installed apps in the Django project
  'django_prometheus',
]

MIDDLEWARE = [
  'django_prometheus.middleware.PrometheusBeforeMiddleware',  # MUST be 1st
  # All the other middleware in the Django project
  'django_prometheus.middleware.PrometheusAfterMiddleware',   # MUST be last
]
```

```python
# In the main urls.py...

urlpatterns = [
  # All your other url conf patterns...
  path('', include('django_prometheus.urls')),
]
```

With django-prometheus configured all sorts of Django metrics will be available at `[your-apps-domain]/metrics`. 

![metrics](docs/imgs/monitor_03.png)

Now we can track metrics that are relevant and important to us- requests by page name, memory usage, processing, etc.

![metrics-2](docs/imgs/monitor_01.png)

![metrics-3](docs/imgs/monitor_02.png)

## Production environment

Separating development and production environments is an important, industry standard, SOP that ensures higher up time, fewer bugs and better user experience. These incur additional costs and add complexity to the DevOps infrastructure but are essential for balancing data integrity, security and application stability with agile project management, innovation and development. There are several components in place to productionize dispatch-predictions.

#### Separate resources/parallel architecture

Having dedicated resources for each environment is a must- particularly with infrastructure that affects user experience or data. databases and web servers are logical assets to have segregated. Your production data, especially when and where you are the system of record, should not be contaminated with dev data, data made from factories or test data. It will be essential for development to have a sandbox database in which you can create, alter and delete records without any regard for novel production data. Having a development webserver, removed from the production web server, allows the developers to implement features incrementally without inconveniencing users with server errors, broken pages or half deployed tools.

For dispatch-predictions there are two main components and each have separate assets in each environment. For the development environment the database is the local machine's postgres installation. The production database is a postgres based AWS Relational Database Service (RDS). 

#### Environment variables

The various components of the application will use environment variables to distinguish between the two environments. The database engine, host address, username and password are different in the different environments. A `.env` file exists in each environment with values for their respective assets. Application layer logic can use the environment variables to tailor the connections appropriately. 

Additionally, environment variables contain secrets. `.env` files do not enter the git repository and have restrictive permissions for security. Because they are not tracked by git they must be created separately- one for each environment. Among these secrets are the AWS account credentials needed by the application to interact with AWS resources.

#### Branches

Maintaining disparate code branches can also separate development and production environments. All work is performed on the "dev branch." Only when it has been vetted is dev merged with the "prod branch." The resources running in the production environment will only ever work off code in the prod branch. New development will only ever take place on the dev branch.

Branches can also be used to develop new features or to host complex refactors. If a particular patch requires ongoing work it can be developed in parallel while regular updates can continue to occur on the dev branch.

In dispatch-predictions "dev" is the development branch and "master" the production branch. 

#### Continuous integration & continuous delivery (CI/CD)

When it is time to move updates into production a CI/CD pipeline automates the steps necessary to ensure quality patches to the production environment. In dispatch-predictions there are a set of Github actions that trigger resources in the production environment to pull in updates and run cursory checks. If the application fails to compile the new commits will be rolled back- preventing downtime and interruptions to the various services.

The CI/CD pipeline will also install new dependencies and upgrade any packages according to changes in the requirements.txt file. The pipeline will also run any new required database migrations.

The Github action for dispatch-predictions is defined in `.github/workflows/ci.yml`.
