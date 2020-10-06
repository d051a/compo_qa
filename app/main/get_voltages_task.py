import django
import os
import sys
import time
import datetime
import statistics
from collections import deque
sys.path.append("/app/web")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.chaos_utils import ChaosStatisctic
from main.models import Chaos
from main.tasks import add_current_statistic_to_db
from main.tasks_tools import get_current_voltage


def get_full_voltage_statistics():
    voltage_statistics = {}
    get_voltage_try = 1
    while True:
        chaoses = Chaos.objects.exclude(multimeter_ip=None)
        time.sleep(3)
        for chaos in chaoses:
            time.sleep(0.5)
            current_voltage = get_current_voltage(chaos.multimeter_ip)
            if not current_voltage:
                continue

            statistic = ChaosStatisctic(ip=chaos.ip)
            voltage_statistics.setdefault(chaos.pk, deque(maxlen=10000)).append(current_voltage)
            chaos_voltage_stats = voltage_statistics[chaos.pk]
            get_voltage_try += 1
            if get_voltage_try % 60 == 0:
                chaos_voltage_stats.append(current_voltage)
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                voltage_average = statistics.mean(chaos_voltage_stats)
                voltage_min = min(chaos_voltage_stats)
                voltage_max = max(chaos_voltage_stats)
                db_statisctic_row = add_current_statistic_to_db(chaos, statistic)
                db_statisctic_row.voltage_current = current_voltage
                db_statisctic_row.voltage_average = voltage_average
                db_statisctic_row.voltage_max = voltage_max
                db_statisctic_row.save()
                print_str = f'{date_time} Добавлен текущий замер {current_voltage}.' \
                    f'Average: {voltage_average:.4f} ' \
                    f'Min: {voltage_min:.4f} ' \
                    f'Max: {voltage_max:.4f} \n'
                print(print_str)


if __name__ == "__main__":
    get_full_voltage_statistics()