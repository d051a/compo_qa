import requests
import time


import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from main.models import Queue, Statistic, MetricReport, Chaos, NetCompilationStat, DrawImgsStat, DrawImgsReport
from chaos.chaos_utils import ChaosStatisctic
from chaos.chaos_utils import Utils as utils


chaos_ip_address = '172.16.26.96'
chaos_port = '19872'


def get_chaos_api_request(request):
    result = {}
    try:
        r = requests.get(f"http://{'127.0.0.1' if not chaos_ip_address else chaos_ip_address}:{chaos_port}/{request}")
        result = r.text
    except requests.exceptions.ConnectionError:
        print(f'Cannot connect to {chaos_ip_address}')
        return 0
    except Exception as e:
        print(e)
        return 0
    finally:
        return result


def main():
    print('start')
    report_id = 1
    chaos_id = 4
    draw_report_id = 1
    metric_report = MetricReport.objects.get(pk=report_id)
    draw_images_report = DrawImgsReport.objects.get(pk=draw_report_id)
    chaos = Chaos.objects.get(pk=chaos_id)
    statistic = ChaosStatisctic(ip=chaos.ip)

    report_start_time = metric_report.create_date_time
    now = '2020-08-18 12:03:20.969805'
    while True:
        current_time = utils.get_time_now()
        elapsed_time = utils.get_time_delta(current_time, report_start_time, "{hours}:{minutes}:{seconds}")
        db_statisctic_row = Statistic(
            total_nodes=statistic.total_nodes,
            inaccessible_nodes=statistic.inaccessible_nodes,
            total_number_routes=statistic.total_number_routes,
            maximum_road_length=statistic.maximum_route_length,
            average_route_length=statistic.average_route_length,
            accessible_nodes_percent=statistic.accessible_nodes_percent,
            elapsed_time=statistic.elapsed_time,
            total_esl=statistic.total_esl,
            online_esl=statistic.online_esl,
            images_in_transit=statistic.images_in_transit,
            images_in_draw=statistic.images_in_draw,
            images_in_resend_queue=statistic.images_in_resend_queue,
            images_succeeded=statistic.images_succeeded,
            images_failed=statistic.images_failed,
            currently_scanning=statistic.currently_scanning,
            network_mode=statistic.network_mode,
            connects=statistic.connects,
        )
        # db_net_compilation_row = NetCompilationStat(
        #     chaos_id=chaos,
        #     metric_report_id=metric_report,
        #     online_esl=statistic.online_esl,
        #     compilation_percent=statistic.get_net_compilation_percent(),
        #     elapsed_time=elapsed_time,
        # )
        # db_drawed_images_row = DrawImgsStat(
        #     draw_imgs_report=draw_images_report,
        #     online_esl=statistic.online_esl,
        #     images_succeeded=statistic.images_succeeded,
        #     drawed_percent=statistic.get_drawed_images_percent(),
        #     elapsed_time=elapsed_time,
        # )
        # db_net_compilation_row.save()
        # db_drawed_images_row.save()
        db_statisctic_row.save()
        time.sleep(10)


if __name__ == '__main__':
    main()


