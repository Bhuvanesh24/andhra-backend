# Generated by Django 5.1.3 on 2024-12-12 01:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0009_delete_landuse_usagepredictiondist_agriculuture_and_more'),
    ]

    operations = [
        # migrations.DeleteModel(
        #     name='LandUse',
        # ),
        migrations.RemoveField(
            model_name='usagepredictiondist',
            name='agriculuture',
        ),
        migrations.RemoveField(
            model_name='usagepredictiondist',
            name='built_up',
        ),
        migrations.RemoveField(
            model_name='usagepredictiondist',
            name='forest',
        ),
        migrations.RemoveField(
            model_name='usagepredictiondist',
            name='wasteland',
        ),
        migrations.RemoveField(
            model_name='usagepredictiondist',
            name='waterbodies',
        ),
        migrations.RemoveField(
            model_name='usagepredictiondist',
            name='wetlands',
        ),
    ]
