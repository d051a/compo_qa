import django
import os
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.models import MetricReport, Chaos, NetCompilationStat, NetCompileReport
from chaos.chaos_utils import ChaosStatisctic
from chaos.chaos_utils import Utils as utils




chaos_ip_address = '172.16.26.96'
chaos_port = '19872'

report_id = 3
chaos_id = 1

drawed_percent_points = [10, 20, 50, 75, 90, 95, 96, 97, 98, 99, 100]


def add_netcompile_row_to_db(chaos, report, statistic, elapsed_time):
    db_net_compilation_row = NetCompilationStat(
        chaos=chaos,
        net_compile_report=report,
        online_esl=statistic.online_esl,
        compilation_percent=statistic.get_net_compilation_percent(),
        elapsed_time=elapsed_time,
    )
    db_net_compilation_row.save()


def main(id_report, id_chaos):
    db_metric_report_object = NetCompileReport.objects.get(pk=id_report)
    db_chaos_object = Chaos.objects.get(pk=id_chaos)
    report_start_time = db_metric_report_object.create_date_time
    while True:
        current_time = utils.get_time_now()
        elapsed_time = utils.get_time_delta(current_time, report_start_time, "{hours}:{minutes}:{seconds}")
        current_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        net_compilation_percernt = current_statistic_data.get_net_compilation_percent()
        add_netcompile_row_to_db(db_chaos_object, db_metric_report_object, current_statistic_data, elapsed_time)
        print(net_compilation_percernt)
        print(f'Добавлены новые метрики. Время:{current_time} Разница: {elapsed_time}', )
        if net_compilation_percernt == 100:
            break
        time.sleep(10)


if __name__ == '__main__':
    main(report_id, chaos_id)