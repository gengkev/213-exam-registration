# Generated by Django 2.0.6 on 2018-08-07 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0016_auto_20180802_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='examregistration',
            name='checkin_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='examregistration',
            name='checkin_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='registration.Room'),
        ),
        migrations.AddField(
            model_name='examregistration',
            name='checkin_time_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examregistration',
            name='checkin_time_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='examregistration',
            name='checkin_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='registration.CourseUser'),
        ),
        migrations.AddField(
            model_name='historicalexamregistration',
            name='checkin_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='historicalexamregistration',
            name='checkin_room',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='registration.Room'),
        ),
        migrations.AddField(
            model_name='historicalexamregistration',
            name='checkin_time_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalexamregistration',
            name='checkin_time_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalexamregistration',
            name='checkin_user',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='registration.CourseUser'),
        ),
        migrations.AlterField(
            model_name='courseuser',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], default='r', max_length=1),
        ),
        migrations.AlterField(
            model_name='courseuser',
            name='user_type',
            field=models.CharField(choices=[('i', 'Instructor'), ('s', 'Student')], default='s', max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalcourseuser',
            name='exam_slot_type',
            field=models.CharField(choices=[('r', 'Normal'), ('e', 'Extended time')], default='r', max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalcourseuser',
            name='user_type',
            field=models.CharField(choices=[('i', 'Instructor'), ('s', 'Student')], default='s', max_length=1),
        ),
    ]
