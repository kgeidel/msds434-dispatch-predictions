# Generated by Django 5.1.5 on 2025-01-31 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0002_alter_historicalincident_num_alter_incident_num_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incident',
            options={'ordering': ['-dtg_alarm']},
        ),
    ]
