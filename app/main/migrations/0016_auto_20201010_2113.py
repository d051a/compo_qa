# Generated by Django 3.1 on 2020-10-10 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20201009_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='drawimgsreport',
            name='task_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Celery task ID'),
        ),
        migrations.AddField(
            model_name='metricreport',
            name='task_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Celery task ID'),
        ),
        migrations.AddField(
            model_name='netcompilereport',
            name='task_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Celery task ID'),
        ),
    ]
