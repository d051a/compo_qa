# Generated by Django 3.1 on 2020-09-25 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chaos',
            name='config',
            field=models.TextField(blank=True, null=True, verbose_name='Конфиг хаоса'),
        ),
    ]
