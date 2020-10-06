# Generated by Django 3.1 on 2020-10-05 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_statistic_voltage_max'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='bat_reserved1',
            field=models.IntegerField(blank=True, null=True, verbose_name='bat_reserved1'),
        ),
        migrations.AddField(
            model_name='statistic',
            name='bat_reserved2',
            field=models.IntegerField(blank=True, null=True, verbose_name='bat_reserved2'),
        ),
        migrations.AddField(
            model_name='statistic',
            name='bat_reserved3',
            field=models.IntegerField(blank=True, null=True, verbose_name='bat_reserved3'),
        ),
        migrations.AddField(
            model_name='statistic',
            name='bat_reserved4',
            field=models.IntegerField(blank=True, null=True, verbose_name='bat_reserved4'),
        ),
    ]