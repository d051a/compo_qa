import django
import os
import sys
import json
import time
import threading
from datetime import datetime
sys.path.append("/app/web")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.chaos_utils import ChaosStatisctic
from main.models import Chaos
from main.chaos_utils import Utils as utils
from main.tasks.tasks_tools import add_current_statistic_to_db


def get_status_ex(chaos):
    output_data = utils.run_remote_command(chaos.ip,
                                           chaos.login,
                                           chaos.password,
                                           chaos.ssh_port,
                                           f'/var/Componentality/Chaos/get_status_ex.py -jan'
                                           )
    return output_data


def get_bat_reserved(input_data):
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    try:
        esl_statistics = json.loads(input_data[0])
    except json.decoder.JSONDecodeError:
        print(f'{time_now} FAIL: Это не JSON. Что-то пошло не так. Данные не получены...')
        print(f'STDOUT: {input_data[0]}: STDERR: {input_data[1]}')
        return None
    except TypeError:
        return None
    # esl_statistics = json.loads(input_data)
    bat_reserved_quantities = {1: 0, 2: 0, 3: 0, 4: 0}
    for esl_stat in esl_statistics.keys():
        bat_reserved = esl_statistics[esl_stat].get('bat_reserved')
        if bat_reserved is None:
            continue
        # bat_reserved_quantities.setdefault(bat_reserved, 0)
        bat_reserved_quantities[bat_reserved] += 1
    return bat_reserved_quantities


def run_get_status_ex_task(chaos):
    global run_tasks
    get_status_ex_data = get_status_ex(chaos)
    # with open('get_status_ex.txt', 'r') as file:
    #     get_status_ex_data = file.read()
    bat_reserved_quantities = get_bat_reserved(get_status_ex_data)
    if bat_reserved_quantities is None:
        run_tasks[chaos.pk] = ['STOPPED']
    else:
        statistic = ChaosStatisctic(ip=chaos.ip)
        db_statisctic_row = add_current_statistic_to_db(chaos, statistic)
        for bat_reserved_count in bat_reserved_quantities.keys():
            bat_reserved_quantity = bat_reserved_quantities[bat_reserved_count]
            setattr(db_statisctic_row, f'bat_reserved{bat_reserved_count}', bat_reserved_quantity)
        db_statisctic_row.save()
        run_tasks[chaos.pk] = ['STOPPED']


def main():
    global run_tasks
    while True:
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        chaoses = Chaos.objects.filter(bat_reserved=True).exclude(multimeter_ip=None)
        print(f"{time_now} Очередной этап получения данных... Значения 'bat_reserved' собираются с {len(chaoses)} устройств(а).")
        for chaos in chaoses:
            run_tasks.setdefault(chaos.pk, ['STOPPED'])
            task_status = run_tasks[chaos.pk]
            print(run_tasks)
            if task_status == ['STOPPED']:
                run_tasks[chaos.pk] = ['WORKING']
                task = threading.Thread(target=run_get_status_ex_task, args=(chaos,))
                task.start()
            elif task_status == ['WORKING']:
                continue
            print(run_tasks)
        time.sleep(600)


if __name__ == '__main__':
    run_tasks = {}
    main()
