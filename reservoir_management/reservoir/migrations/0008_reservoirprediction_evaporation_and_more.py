# Generated by Django 5.1.3 on 2024-12-11 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservoir', '0007_reservoirscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservoirprediction',
            name='evaporation',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='reservoirprediction',
            name='rainfall',
            field=models.FloatField(null=True),
        ),
    ]
