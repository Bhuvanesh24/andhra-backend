# Generated by Django 5.1.3 on 2024-11-25 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservoir', '0002_alter_reservoirdata_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservoir',
            name='district',
        ),
        migrations.AddField(
            model_name='reservoir',
            name='name',
            field=models.CharField(default='Unknown', max_length=200),
        ),
    ]
