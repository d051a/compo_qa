# Generated by Django 3.1 on 2020-10-31 10:28

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_chaos_grafana_dashboard_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_num', models.CharField(max_length=30, null=True, unique=True, verbose_name='Номер версии')),
                ('date_time', models.DateTimeField(blank=True, default=django.utils.timezone.localtime, null=True, verbose_name='Дата и время создания')),
            ],
            options={
                'verbose_name': 'Версия',
                'verbose_name_plural': 'Версии',
                'ordering': ['-pk'],
            },
        ),
        migrations.AddField(
            model_name='chaos',
            name='hardware_config',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Конфигурация системы'),
        ),
        migrations.AddField(
            model_name='chaos',
            name='shields_num',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Номера щитов'),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(blank=True, default=django.utils.timezone.localtime, null=True, verbose_name='Дата и время создания')),
                ('shields_num', models.CharField(blank=True, max_length=50, null=True, verbose_name='Номера щитов')),
                ('hardware_config', models.CharField(blank=True, max_length=400, null=True, verbose_name='Конфигурация системы')),
                ('total_esl', models.IntegerField(blank=True, null=True, verbose_name='Количество ценников стенда, шт')),
                ('dd_nums', models.CharField(blank=True, max_length=350, null=True, verbose_name='Количество РУ, шт')),
                ('dd_configuration', models.CharField(blank=True, max_length=350, null=True, verbose_name='Конфигурация РУ')),
                ('dd_dongles_num', models.CharField(blank=True, max_length=150, null=True, verbose_name='Количество донглов на РУ, шт')),
                ('version_sum', models.CharField(blank=True, max_length=30, null=True, verbose_name='Версия СУМ')),
                ('version_chaos', models.CharField(blank=True, max_length=30, null=True, verbose_name='Версия Хаоса')),
                ('chaos_configuration', models.TextField(blank=True, null=True, verbose_name='Конфигурация Хаоса')),
                ('tree_floor_num', models.IntegerField(blank=True, null=True, verbose_name='Число этажей дерева')),
                ('version_driver', models.CharField(blank=True, max_length=30, null=True, verbose_name='Версия драйвера')),
                ('version_esl_firmware', models.CharField(blank=True, max_length=250, null=True, verbose_name='Версия прошивки ЭЦ')),
                ('version_esl_hw', models.CharField(blank=True, max_length=250, null=True, verbose_name='HW версия ЭЦ')),
                ('version_dongles_hw', models.CharField(blank=True, max_length=250, null=True, verbose_name='HW версия донглов')),
                ('chaos', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.chaos', verbose_name='Стенд')),
                ('drawimgs_report', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.drawimgsreport', verbose_name='Отчет об отрисовке')),
                ('metric_report', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.metricreport', verbose_name='Общий отчет')),
                ('netcompile_report', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.netcompilereport', verbose_name='Отчет о сборке сети')),
                ('version_num', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.version', verbose_name='Версия')),
            ],
            options={
                'verbose_name': 'Конфигурация',
                'verbose_name_plural': 'Конфигурации',
                'ordering': ['-pk'],
            },
        ),
        migrations.AddField(
            model_name='drawimgsreport',
            name='config',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.configuration', verbose_name='Конфигурация'),
        ),
        migrations.AddField(
            model_name='metricreport',
            name='config',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.configuration', verbose_name='Конфигурация'),
        ),
        migrations.AddField(
            model_name='netcompilereport',
            name='config',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.configuration', verbose_name='Конфигурация'),
        ),
    ]