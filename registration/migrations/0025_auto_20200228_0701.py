# Generated by Django 2.2.10 on 2020-02-28 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0024_auto_20200228_0506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examslot',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], default='r', max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalexamslot',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], default='r', max_length=1),
        ),
    ]
