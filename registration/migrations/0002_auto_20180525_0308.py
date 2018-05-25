# Generated by Django 2.0.2 on 2018-05-25 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examregistration',
            name='course_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_registration_set', to='registration.CourseUser'),
        ),
        migrations.AlterField(
            model_name='examregistration',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_registration_set', to='registration.Exam'),
        ),
        migrations.AlterField(
            model_name='examregistration',
            name='time_slot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_registrations', to='registration.TimeSlot'),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_slot_set', to='registration.Exam'),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='rooms',
            field=models.ManyToManyField(blank=True, to='registration.Room'),
        ),
    ]