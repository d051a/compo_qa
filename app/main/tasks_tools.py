from main.models import NetCompilationStat, NetCompileReport, DrawImgsReport, \
    DrawImgsStat, Chaos, Statistic, MetricReport
import time
import requests
import json
from datetime import datetime
from chaos.chaos_utils import Utils as utils


def check_host_alive(chaos_ip, slave_ip, slave_port):
    rq_cnt = 100500
    time_out = 3
    url = f'http://{slave_ip}:{slave_port}'
    if chaos_ip == '127.0.0.1':
        url = f'http://{chaos_ip}:{slave_port}'
    try:
        request = requests.post(url, json={'command': 'ping', 'request-id': rq_cnt}, timeout=time_out)
    except:
        print('Driver at %s is not available, no ping' % url)
        return False
    try:
        request = requests.post(url, json={'command': 'list-roots', 'request-id': rq_cnt}, timeout=time_out)
        rq_cnt += 1
        roots = json.loads(request.text)["roots"]
        print("Driver at %s roots: %s" % (url, ', '.join(roots)))
    except:
        print('Driver at %s is not available, no roots' % url)
        return False
    return True


def get_ips_by_names(name_port_list, device_credentials):
    device_ssh_address = device_credentials['ip']
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    ip_port = {}
    for address in name_port_list:
        host_name, port = address.split(':')
        ip = utils.run_remote_command(
            device_ssh_address,
            ssh_user_name,
            ssh_user_password,
            ssh_port,
            f'net lookup {host_name}')[0].rstrip()
        if host_name == '127.0.0.1':
            ip_port[f'{device_ssh_address}:{port}'] = ''
            continue
        ip_port[f'{ip}:{port}'] = ''
    return ip_port


def get_default_devices(device_credentials):
    device_ssh_address = device_credentials['ip']
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    run_command = utils.run_remote_command(device_ssh_address, ssh_user_name, ssh_user_password, ssh_port,
                                           'cat /var/Componentality/Chaos/chaos_config.json')
    if run_command == ('', ''):
        return None
    chaos_config = json.loads(run_command[0])
    names_ports = chaos_config['DEFAULT_RSERVERS']
    return names_ports


def check_all_alive(rebooted_devices_ips_ports, chaos_ip, max_work_time_minutes=5):
    time_start = datetime.now()
    while rebooted_devices_ips_ports:
        time.sleep(1)
        time_now = datetime.now()
        elapsed_time = (time_now - time_start).total_seconds() / 60
        if elapsed_time > max_work_time_minutes:
            print(
                f'Устройства перезагружаются дольше чем {max_work_time_minutes} минут. '
                f'Процесс перезапуска остановлен!')
            return False
        for address in list(rebooted_devices_ips_ports):
            ip, port = address.split(':')
            alive = check_host_alive(chaos_ip, ip, port)
            if alive:
                rebooted_devices_ips_ports.pop(address)
    print('Хаос и все слейвы перезапущены! Все живы!')
    return True


def reboot_devices_list(devices_ips_ports, device_credentials):
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    devices_ips = [device.split(':')[0] for device in devices_ips_ports]
    for ip_address in set(devices_ips):
        try:
            print(f'Инициация перезагрузки устройства: {ip_address}')
            run_command = utils.run_remote_command(ip_address, ssh_user_name, ssh_user_password, ssh_port,
                                                   f'echo {ssh_user_password}|sudo -S sudo reboot')
            return True
        except:
            print(f'Неудалось инициировать перезагрузку устройства: {ip_address}')
            return False


def add_current_statistic_to_db(db_chaos_object, current_chaos_statistic_data, metric_report=None):
    db_statisctic_row = Statistic.objects.create(
        chaos=db_chaos_object,
        metric_report=metric_report,
        total_nodes=current_chaos_statistic_data.total_nodes,
        inaccessible_nodes=current_chaos_statistic_data.inaccessible_nodes,
        total_number_routes=current_chaos_statistic_data.total_number_routes,
        maximum_road_length=current_chaos_statistic_data.maximum_route_length,
        average_route_length=current_chaos_statistic_data.average_route_length,
        accessible_nodes_percent=current_chaos_statistic_data.accessible_nodes_percent,
        elapsed_time=current_chaos_statistic_data.elapsed_time,
        total_esl=current_chaos_statistic_data.total_esl,
        online_esl=current_chaos_statistic_data.online_esl,
        images_in_transit=current_chaos_statistic_data.images_in_transit,
        images_in_draw=current_chaos_statistic_data.images_in_draw,
        images_in_resend_queue=current_chaos_statistic_data.images_in_resend_queue,
        images_succeeded=current_chaos_statistic_data.images_succeeded,
        images_failed=current_chaos_statistic_data.images_failed,
        currently_scanning=current_chaos_statistic_data.currently_scanning,
        network_mode=current_chaos_statistic_data.network_mode,
        connects=current_chaos_statistic_data.connects,
    )
    db_statisctic_row.save()


def add_net_compilation_statistics_to_db(db_chaos_object,
                                         db_metric_report_object,
                                         current_chaos_statistic_data,
                                         net_compilation_percernt,
                                         elapsed_time):
    db_net_compilation_row = NetCompilationStat(
        chaos=db_chaos_object,
        net_compile_report=db_metric_report_object,
        online_esl=current_chaos_statistic_data.online_esl,
        compilation_percent=net_compilation_percernt,
        elapsed_time=elapsed_time,
    )
    db_net_compilation_row.save()


def add_draw_images_statistics_to_db(db_chaos_object,
                                     db_draw_imgs_object,
                                     current_chaos_statistic_data,
                                     drawed_percent_step,
                                     elapsed_time):
    db_drawed_images_row = DrawImgsStat(
        chaos=db_chaos_object,
        draw_imgs_report=db_draw_imgs_object,
        online_esl=current_chaos_statistic_data.online_esl,
        percent_step=drawed_percent_step,
        images_succeeded=current_chaos_statistic_data.images_succeeded,
        drawed_percent=current_chaos_statistic_data.get_drawed_images_percent(),
        elapsed_time=elapsed_time,
    )
    db_drawed_images_row.save()


def get_fact_percent(dividend, fact_total_esl):
    fact_percent = (dividend / fact_total_esl) * 100
    return float(f"{fact_percent:.2f}")


def get_net_compilation_percernt(curent_stats_data, fact_total_esl):
    if fact_total_esl:
        net_compilation_percernt = (curent_stats_data.online_esl / fact_total_esl) * 100
        return float(f"{net_compilation_percernt:.2f}")
    else:
        net_compilation_percernt = curent_stats_data.get_net_compilation_percent()
        return net_compilation_percernt


def get_drawed_images_percent(curent_stats_data, fact_total_esl):
    if fact_total_esl:
        drawed_images_percent = (curent_stats_data.images_succeeded / fact_total_esl) * 100
        return float(f"{drawed_images_percent:.2f}")
    else:
        drawed_images_percent = curent_stats_data.get_drawed_images_percent()
        return drawed_images_percent


def get_not_drawed_images(curent_stats_data, fact_total_esl):
    if fact_total_esl:
        not_drawed_images = fact_total_esl - curent_stats_data.images_succeeded
    else:
        not_drawed_images = curent_stats_data.total_esl - curent_stats_data.images_succeeded
        return not_drawed_images


def save_draw_imgs_final_status_and_data(db_draw_imgs_object, curent_stats_data, status):
    db_draw_imgs_object.not_drawed_esl = get_not_drawed_images(curent_stats_data, db_draw_imgs_object.fact_total_esl)
    db_draw_imgs_object.not_drawed_esl = curent_stats_data.images_succeeded
    db_draw_imgs_object.status = status
    db_draw_imgs_object.date_time_finish = datetime.now()
    db_draw_imgs_object.save()


def save_net_compilation_final_status_and_data(db_net_compilation_object, status):
    db_net_compilation_object.status = status
    db_net_compilation_object.date_time_finish = datetime.now()
    db_net_compilation_object.save()


def set_db_object_attribute(db_object, attrubute_name, value):
    setattr(db_object, attrubute_name, value)
    db_object.save()


def start_drawing_images(device_credentials):
    connection = utils.run_remote_command(device_credentials['ip'],
                                          device_credentials['login'],
                                          device_credentials['password'],
                                          device_credentials['port'],
                                          f'/var/Componentality/Chaos/Highlight_ESL.py -s RBWX'
                                          )
    return connection


if __name__ == '__main__':
    chaos_credentials = {'ip': '172.16.26.210',
                         'login': 'pi',
                         'password': 'CompoM123',
                         'port': 22,
                         }
