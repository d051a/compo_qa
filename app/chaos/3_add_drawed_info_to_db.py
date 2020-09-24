import django
import os
import time
import sys
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.models import MetricReport, Chaos, DrawImgsStat, DrawImgsReport
from chaos.chaos_utils import ChaosStatisctic
from chaos.chaos_utils import Utils as utils


server_ssh_address = '172.16.27.169'
ssh_port = '22'
ssh_user_name = 'pi'
ssh_user_password = 'CompoM123'

drawed_percent_points = [10, 20, 50, 75, 90, 95, 96, 97, 98, 99, 100]


def add_drawed_row_to_db(chaos, report, statistic, elapsed_time, percent_step):
    db_drawed_images_row = DrawImgsStat(
        chaos=chaos,
        draw_imgs_report=report,
        online_esl=statistic.online_esl,
        percent_step=percent_step,
        images_succeeded=statistic.images_succeeded,
        drawed_percent=statistic.get_drawed_images_percent(),
        elapsed_time=elapsed_time,
    )
    db_drawed_images_row.save()


def main(ip_chaos):
    utils.run_remote_command(server_ssh_address, ssh_user_name, ssh_user_password, ssh_port, f'/var/Componentality/Chaos/Highlight_ESL.py -s RBWX')
    db_chaos_object = Chaos.objects.get(ip=ip_chaos)
    db_metric_report_object = DrawImgsReport(chaos=db_chaos_object)
    db_metric_report_object.save()

    report_start_time = db_metric_report_object.create_date_time
    current_step = 0
    last_step = len(drawed_percent_points)-1
    while True:

        current_time = utils.get_time_now()
        elapsed_time = utils.get_time_delta(current_time, report_start_time, "{hours}:{minutes}:{seconds}")
        current_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        drawed_images_percent = current_statistic_data.get_drawed_images_percent()
        print(f'Текущий процент: {drawed_images_percent} Процент шага: {drawed_percent_points[current_step]}')
        if drawed_images_percent >= drawed_percent_points[current_step]:
            add_drawed_row_to_db(db_chaos_object, db_metric_report_object, current_statistic_data, elapsed_time, drawed_percent_points[current_step])
            setattr(db_metric_report_object, f'p{drawed_percent_points[current_step]}', elapsed_time)
            db_metric_report_object.save()
            print(f'Добавлены новые метрики. Время: {current_time} Разница: {elapsed_time}', )
            current_step += 1
        if current_step > last_step:
            break
        time.sleep(5)


if __name__ == '__main__':
    main(server_ssh_address)
