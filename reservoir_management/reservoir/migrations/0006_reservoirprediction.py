# Generated by Django 5.1.3 on 2024-11-28 05:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0005_rainfall'),
        ('reservoir', '0005_reservoirdata_reservoir_r_reservo_f400bc_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservoirPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('gross_capacity', models.FloatField()),
                ('current_storage', models.FloatField()),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecast.district')),
                ('reservoir', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservoir.reservoir')),
            ],
            options={
                'indexes': [models.Index(fields=['reservoir', 'year'], name='reservoir_r_reservo_c53e41_idx')],
            },
        ),
    ]
