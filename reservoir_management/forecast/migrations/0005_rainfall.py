# Generated by Django 5.1.3 on 2024-11-28 04:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0004_alter_usage_reservoir'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rainfall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('normal', models.FloatField()),
                ('actual', models.FloatField()),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecast.district')),
            ],
        ),
    ]
