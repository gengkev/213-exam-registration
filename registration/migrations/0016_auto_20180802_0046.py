# Generated by Django 2.0.6 on 2018-08-02 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0015_auto_20180628_2324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='examregistration',
            options={'ordering': ['course_user', 'exam']},
        ),
        migrations.AlterModelOptions(
            name='examslot',
            options={'ordering': ['exam', 'exam_slot_type', 'start_time_slot']},
        ),
        migrations.AlterField(
            model_name='courseuser',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], max_length=1),
        ),
        migrations.AlterField(
            model_name='examslot',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalcourseuser',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalexamslot',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], max_length=1),
        ),
    ]
