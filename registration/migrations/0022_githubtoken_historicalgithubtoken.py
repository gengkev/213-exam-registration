# Generated by Django 3.0.3 on 2020-02-06 06:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0021_auto_20181127_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalGithubToken',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('github_login', models.CharField(max_length=64)),
                ('token_type', models.CharField(max_length=32)),
                ('access_token', models.CharField(max_length=64)),
                ('scope', models.CharField(blank=True, max_length=64)),
                ('authorize_time', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('course_user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='registration.CourseUser')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical github token',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='GithubToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_login', models.CharField(max_length=64)),
                ('token_type', models.CharField(max_length=32)),
                ('access_token', models.CharField(max_length=64)),
                ('scope', models.CharField(blank=True, max_length=64)),
                ('authorize_time', models.DateTimeField(auto_now_add=True)),
                ('course_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='github_token', to='registration.CourseUser')),
            ],
        ),
    ]