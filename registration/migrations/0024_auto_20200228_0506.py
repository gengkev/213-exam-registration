# Generated by Django 3.0.3 on 2020-02-28 05:06

from django.db import migrations, models


def set_reg_count(apps, schema_editor):
    ExamSlot = apps.get_model('registration', 'ExamSlot')
    for exam_slot in ExamSlot.objects.all():
        exam_slot.reg_count = exam_slot.exam_registration_set.count()
        exam_slot.save(update_fields=['reg_count'])


def reverse_set_reg_count(apps, schema_editor):
    # reg_count will be deleted when reversing
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0023_auto_20200226_0501'),
    ]

    operations = [
        migrations.AddField(
            model_name='examslot',
            name='reg_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.RunPython(set_reg_count, reverse_set_reg_count),
        migrations.AddField(
            model_name='historicalexamslot',
            name='reg_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
