# Generated by Django 5.1.5 on 2025-01-26 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalincident',
            name='num',
            field=models.CharField(max_length=11, verbose_name='Call #'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='num',
            field=models.CharField(max_length=11, verbose_name='Call #'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['num', 'dtg_alarm'], name='calls_incid_num_ee366a_idx'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['dtg_alarm'], name='calls_incid_dtg_ala_593cef_idx'),
        ),
        migrations.AddConstraint(
            model_name='incident',
            constraint=models.UniqueConstraint(fields=('num', 'dtg_alarm'), name='unique_incident'),
        ),
    ]
