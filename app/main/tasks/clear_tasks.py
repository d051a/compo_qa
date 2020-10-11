import django
import os
import sys
sys.path.append("/app/web")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.models import MetricReport, DrawImgsReport, NetCompileReport
from django.utils import timezone


status = 'FAIL: Задача была остановлена. В процессе выполнения произошла перезагрузка сервера'
date_time = timezone.localtime()
metric_report_with_task_id = MetricReport.objects.exclude(task_id='').update(
    task_id='', status=status, date_time_finish=date_time)
draw_imgs_report_with_task_id = DrawImgsReport.objects.exclude(task_id='').update(
    task_id='', status=status, date_time_finish=date_time)
net_compile_with_task_id = NetCompileReport.objects.exclude(task_id='').update(
    task_id='', status=status, date_time_finish=date_time)
