# Generated by Django 3.1 on 2020-10-15 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20201014_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='chaos',
            name='dat_file',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='.dat файл выгрузки товаров и цен'),
        ),
    ]
