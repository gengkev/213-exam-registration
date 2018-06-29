# Generated by Django 2.0.6 on 2018-06-28 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0013_auto_20180628_0653'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseuser',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Regular'), ('e', 'Extended time')], default='r', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='examslot',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Regular'), ('e', 'Extended time')], default='r', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalcourseuser',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Regular'), ('e', 'Extended time')], default='r', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalexamslot',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Regular'), ('e', 'Extended time')], default='r', max_length=1),
            preserve_default=False,
        ),
    ]
