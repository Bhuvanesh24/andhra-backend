# Generated by Django 5.1.3 on 2024-11-26 03:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0001_initial'),
        ('reservoir', '0003_remove_reservoir_district_reservoir_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usage',
            name='reservoir',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reservoir.reservoir'),
        ),
    ]
