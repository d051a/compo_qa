import django
import os
import sys

sys.path.append("/app/web")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.models import MetricReport, DrawImgsReport, NetCompileReport
from django.utils import timezone
from datetime import datetime

time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
status = 'FAIL: Задача была остановлена. В процессе выполнения произошла перезагрузка сервера'
date_time = timezone.localtime()
print(f'{time_now} Запущен процесс очистки Celery task IDs для объектов БД...')
try:
    metric_report_with_task_id = MetricReport.objects.exclude(task_id='').update(
        task_id='', status=status, date_time_finish=date_time)
    print(f'{time_now} Завершен процесс очистки task IDs для объектов MetricReports')
    draw_imgs_report_with_task_id = DrawImgsReport.objects.exclude(task_id='').update(
        task_id='', status=status, date_time_finish=date_time)
    print(f'{time_now} Завершен процесс очистки task IDs для объектов DrawImgsReports')
    net_compile_with_task_id = NetCompileReport.objects.exclude(task_id='').update(
        task_id='', status=status, date_time_finish=date_time)
    print(f'{time_now} Завершен процесс очистки task IDs для объектов NetCompileReports')
except:
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    print(f'{time_now} Успешно завершен процесс очистки Celery task IDs для объектов БД.')