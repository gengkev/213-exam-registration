# Generated by Django 2.0.6 on 2018-11-27 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0020_auto_20180808_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='lock_after',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='lock_before',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalexam',
            name='lock_after',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalexam',
            name='lock_before',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
