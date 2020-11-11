import time
import requests
import json
import pyvisa
import os
from main.models import NetCompilationStat, DrawImgsStat, Statistic, NetCompileReport, DrawImgsReport, Chaos,\
    MetricReport, Configuration, Version
from datetime import datetime
from main.chaos_utils import Utils as utils
from main.chaos_utils import ChaosStatisctic, ChaosConfigurationInfo
from conf.settings import BASE_DIR, MEDIA_ROOT
from main.tasks.change_price import dat_file_change_prices
from django.db.utils import IntegrityError
from django.utils import timezone
from django.db.models import Avg


def check_host_alive(chaos_ip, slave_ip, slave_port):
    rq_cnt = 100500
    time_out = 3
    url = f'http://{slave_ip}:{slave_port}'
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    if chaos_ip == '127.0.0.1':
        url = f'http://{chaos_ip}:{slave_port}'
    try:
        request = requests.post(url, json={'command': 'ping', 'request-id': rq_cnt}, timeout=time_out)
    except:
        print(f'{time_now} Driver at %s is not available, no ping' % url)
        return False
    try:
        request = requests.post(url, json={'command': 'list-roots', 'request-id': rq_cnt}, timeout=time_out)
        rq_cnt += 1
        roots = json.loads(request.text)["roots"]
        print(f"{time_now} Driver at {url} roots: {', '.join(roots)}")
    except:
        print(f'{time_now} Driver at {url} is not available, no roots')
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
        return False
    chaos_config = json.loads(run_command[0])
    names_ports = chaos_config['DEFAULT_RSERVERS']
    return names_ports


def check_all_alive(rebooted_devices_ips_ports, chaos_ip, max_work_time_minutes=5):
    time_start = datetime.now()
    while rebooted_devices_ips_ports:
        time.sleep(1)
        time_now = datetime.now()
        elapsed_time = (time_now - time_start).total_seconds() / 60
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        if elapsed_time > max_work_time_minutes:
            print(
                f'{time_now} Устройства перезагружаются дольше чем {max_work_time_minutes} минут. '
                f'Процесс перезапуска остановлен!')
            return False
        for address in list(rebooted_devices_ips_ports):
            ip, port = address.split(':')
            alive = check_host_alive(chaos_ip, ip, port)
            if alive:
                rebooted_devices_ips_ports.pop(address)
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    print(f'{time_now} Хаос и все слейвы перезапущены! Все живы!')
    return True


def reboot_devices_list(devices_ips_ports, device_credentials):
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    devices_ips = [device.split(':')[0] for device in devices_ips_ports]

    for ip_address in set(devices_ips):
        try:
            time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
            print(f'{time_now} Инициация перезагрузки устройства: {ip_address}')
            utils.run_remote_command(ip_address, ssh_user_name, ssh_user_password, ssh_port,
                                     f'echo {ssh_user_password}|sudo -S sudo reboot')
        except:
            time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
            print(f'{time_now} Неудалось инициировать перезагрузку устройства: {ip_address}')
            return False
    return True


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
        network_mode_percent=current_chaos_statistic_data.network_mode_percent,
        connects=current_chaos_statistic_data.connects,
    )
    if db_chaos_object.multimeter_ip:
        curent_voltage = get_current_voltage(db_chaos_object.multimeter_ip)
        if curent_voltage:
            db_statisctic_row.voltage_current = curent_voltage
    db_statisctic_row.save()
    return db_statisctic_row


def add_net_compilation_statistics_to_db(db_chaos_object,
                                         db_metric_report_object,
                                         current_chaos_statistic_data,
                                         net_compilation_percent,
                                         elapsed_time):
    db_net_compilation_row = NetCompilationStat(
        chaos=db_chaos_object,
        net_compile_report=db_metric_report_object,
        online_esl=current_chaos_statistic_data.online_esl,
        compilation_percent=net_compilation_percent,
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


def create_net_compilation_report(metric_report):
    chaos = Chaos.objects.get(pk=metric_report.chaos.pk)
    net_compilation_report = NetCompileReport.objects.create(
        metric_report=metric_report,
        chaos=chaos,
        fact_total_esl=metric_report.fact_total_esl,
        net_compile_limit_mins=metric_report.net_compile_limit_mins,
        net_compile_amount=metric_report.net_compile_amount,
        success_percent=metric_report.net_success_percent,
        status='ACTIVE',
    )
    net_compilation_report.save()
    return net_compilation_report


def create_draw_imgs_report(metric_report):
    chaos = Chaos.objects.get(pk=metric_report.chaos.pk)
    draw_imgs_report = DrawImgsReport.objects.create(
        metric_report=metric_report,
        chaos=chaos,
        fact_total_esl=metric_report.fact_total_esl,
        draw_imgs_limit_mins=metric_report.draw_imgs_limit_mins,
        draw_imgs_amount=metric_report.draw_imgs_amount,
        color=metric_report.color,
        draw_imgs_type=metric_report.draw_imgs_type,
        status='ACTIVE',
    )
    draw_imgs_report.save()
    return draw_imgs_report


def get_fact_percent(dividend, fact_total_esl):
    fact_percent = (dividend / fact_total_esl) * 100
    return float(f"{fact_percent:.2f}")


def get_net_compilation_percent(curent_stats_data, fact_total_esl):
    if fact_total_esl:
        net_compilation_percent = (curent_stats_data.online_esl / fact_total_esl) * 100
        return float(f"{net_compilation_percent:.2f}")
    else:
        net_compilation_percent = curent_stats_data.get_true_net_compilation_percent()
        return net_compilation_percent


def get_drawed_images_percent(curent_stats_data, fact_total_esl):
    if fact_total_esl:
        drawed_images_percent = (curent_stats_data.images_succeeded / fact_total_esl) * 100
        return float(f"{drawed_images_percent:.2f}")
    else:
        drawed_images_percent = curent_stats_data.get_drawed_images_percent()
        return drawed_images_percent


def get_not_drawed_images(curent_stats_data, fact_total_esl):
    not_drawed_images = curent_stats_data.total_esl - curent_stats_data.images_succeeded
    if fact_total_esl:
        not_drawed_images = fact_total_esl - curent_stats_data.images_succeeded
    return not_drawed_images


def save_draw_imgs_final_status_and_data(db_draw_imgs_object, curent_stats_data, status):
    current_time = timezone.localtime()
    elapsed_time = utils.get_time_delta(current_time,
                                        db_draw_imgs_object.create_date_time,
                                        "{hours}:{minutes}:{seconds}")
    db_draw_imgs_object.elapsed_time = elapsed_time
    db_draw_imgs_object.final_percent = curent_stats_data.get_drawed_images_percent()
    db_draw_imgs_object.not_drawed_esl = get_not_drawed_images(curent_stats_data, db_draw_imgs_object.fact_total_esl)
    db_draw_imgs_object.drawed_esl = curent_stats_data.images_succeeded
    db_draw_imgs_object.status = status
    db_draw_imgs_object.task_id = ''
    db_draw_imgs_object.date_time_finish = timezone.localtime()
    db_draw_imgs_object.save()


def save_net_compilation_final_status_and_data(db_net_compilation_object, status, net_compilation_percent):
    current_time = timezone.localtime()
    elapsed_time = utils.get_time_delta(current_time,
                                        db_net_compilation_object.create_date_time,
                                        "{hours}:{minutes}:{seconds}")
    db_net_compilation_object.elapsed_time = elapsed_time
    db_net_compilation_object.final_percent = net_compilation_percent
    db_net_compilation_object.status = status
    db_net_compilation_object.task_id = ''
    db_net_compilation_object.date_time_finish = timezone.localtime()
    db_net_compilation_object.save()


def set_db_object_attribute(db_object, attrubute_name, value):
    if '.' in attrubute_name:
        attrubute_name = attrubute_name.replace('.', '')
    setattr(db_object, attrubute_name, value)
    db_object.save()


def start_drawing_images(device_credentials, esl_color):
    connection = utils.run_remote_command_no_wait(device_credentials['ip'],
                                                  device_credentials['login'],
                                                  device_credentials['password'],
                                                  device_credentials['port'],
                                                  f'/var/Componentality/Chaos/Highlight_ESL.py -s {esl_color}'
                                                  )
    return connection


def get_chaos_config(device_credentials):
    config_data = utils.run_remote_command(device_credentials['ip'],
                                           device_credentials['login'],
                                           device_credentials['password'],
                                           device_credentials['port'],
                                           f'cat /var/Componentality/Chaos/chaos_config.json'
                                           )
    if config_data is None:
        return None
    try:
        config_json = json.loads(config_data[0])
    except json.decoder.JSONDecodeError:
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f'{time_now} FAIL: Это не JSON. Что-то пошло не так. Данные не получены...')
        print(f'STDOUT: {config_data[0]}: STDERR: {config_data[1]}')
        return None
    except TypeError:
        return None
    return config_json


def stop_chaos_webcore(device_credentials):
    device_ssh_address = device_credentials['ip']
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    print(f'{time_now} Инициация остановки chaos_webcore ')
    run_command = utils.run_remote_command(device_ssh_address, ssh_user_name, ssh_user_password, ssh_port,
                                           f'echo {ssh_user_password}|sudo -S sudo systemctl stop chaos_webcore')
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    if run_command == ('', ''):
        print(f'{time_now} chaos_webcore успешно остановлен')
        return True
    else:
        print(f'{time_now} chaos_webcore не остановлен. Что-то пошло не так')
        return run_command[1]


def start_chaos_webcore(device_credentials):
    device_ssh_address = device_credentials['ip']
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")

    print(f'{time_now} Инициация запуска chaos_webcore')
    run_command = utils.run_remote_command(device_ssh_address, ssh_user_name, ssh_user_password, ssh_port,
                                           f'echo {ssh_user_password}|sudo -S sudo systemctl start chaos_webcore')
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    if run_command == ('', ''):
        print(f'{time_now} Сервис chaos_webcore успешно запущен')
        return True
    else:
        print(f'{time_now} Сервис chaos_webcore не запущен. Что-то пошло не так. ERROR: {run_command[1]}')
        return run_command[1]


def start_storesvc_service(device_credentials):
    device_ssh_address = device_credentials['ip']
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")

    print(f'{time_now} Инициация запуска службы storesvc ')
    run_command = utils.run_remote_command(device_ssh_address, ssh_user_name, ssh_user_password, ssh_port,
                                           f'echo {ssh_user_password}|sudo -S sudo service storesvc start')
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    if run_command == ('', ''):
        print(f'{time_now} Служба storesvc успешно запущена')
        return True
    else:
        print(f'{time_now} Служба storesvc не запущена. Что-то пошло не так. ERROR: {run_command[1]}')
        return run_command[1]


def stop_storesvc_service(device_credentials):
    device_ssh_address = device_credentials['ip']
    ssh_user_name = device_credentials['login']
    ssh_user_password = device_credentials['password']
    ssh_port = device_credentials['port']
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")

    print(f'{time_now} Инициация остановки службы storesvc ')
    run_command = utils.run_remote_command(device_ssh_address, ssh_user_name, ssh_user_password, ssh_port,
                                           f'echo {ssh_user_password}|sudo -S sudo service storesvc stop')
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    if run_command == ('', ''):
        print(f'{time_now} Служба storesvc успешно остановлена')
        return True
    else:
        print(f'{time_now} Служба storesvc не остановлена. Что-то пошло не так. ERROR: {run_command[1]}')
        return run_command[1]


def sent_request(ip, url_path):
    final_result = {}
    url = f'http://{ip}:19872/{url_path}'
    try:
        r = requests.get(url)
        result = r.text
        final_result['result'] = result
        final_result['code'] = 0
    except requests.exceptions.ConnectionError:
        print(f'Cannot connect {url}')
        final_result['result'] = False
        final_result['code'] = 503
    except Exception as error:
        print(error)
        final_result['result'] = error
        final_result['code'] = 500
    finally:
        return final_result


def reset_send_queue(chaos_ip):
    response = sent_request(chaos_ip, 'reset_send_queue')
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    if response['result'] == 'true':
        print(f'{time_now} Успешный сброс очереди')
        return True
    else:
        return False


def get_current_voltage(multimeter_ip):
    """
    Simple program to get the current voltage value for the "HMC8012 Digital Multimeter" \n
    :param multimeter_ip: device ip-address \n
    :return: float \n
    EXAMPLE:
    python get_voltage.py "127.0.0.1" -n 2
    """
    rm = pyvisa.ResourceManager()
    rm.list_resources()
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    try:
        inst = rm.open_resource(f'TCPIP::{multimeter_ip}::INSTR')
    except pyvisa.errors.VisaIOError:
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f'{time_now} VI_ERROR_RSRC_NFOUND (-1073807343): '
              'Insufficient location information or the requested device or resource is not present in the system. '
              'CHECK CONNECTION TO DEVICE!')
        return None
    except ConnectionRefusedError:
        print(f'{time_now} ERROR: Connection to multimeter refused')
        return None
    except Exception as error:
        print(f'{time_now} ERROR: {error}')
        return None
    voltage = inst.query("FETCh?")
    inst.close()
    return float(voltage)


def net_compilation_init(chaos_credentials, net_compile_report):
    # инициализация сборки сети
    print(f"Инициирована новая сборка сети на устройстве {chaos_credentials['ip']}")
    net_compilation_percent = 0
    server_names_ports = get_default_devices(chaos_credentials)
    if not server_names_ports:
        status = f"FAIL: Не удалось получить DEFAULT_RSERVERS c устройства {chaos_credentials['ip']}"
        save_net_compilation_final_status_and_data(net_compile_report, status, net_compilation_percent)
        return False
    servers_ips_ports = get_ips_by_names(server_names_ports, chaos_credentials)
    stop_chaos_webcore(chaos_credentials)
    if not reboot_devices_list(servers_ips_ports, chaos_credentials):
        status = 'FAIL: Не удалось инициировать перезагрузку одного или нескольких устройств'
        save_net_compilation_final_status_and_data(net_compile_report, status, net_compilation_percent)
        return False
    time.sleep(30)
    if not check_all_alive(servers_ips_ports, chaos_credentials['ip'], 5):
        status = 'FAIL: Одного или несколько устройств недоступно после перезагрузки'
        save_net_compilation_final_status_and_data(net_compile_report, status, net_compilation_percent)
        return False
    time.sleep(60)
    stop_storesvc_service(chaos_credentials)
    start_chaos_webcore(chaos_credentials)
    return True


def net_compilation_get_statistics(net_compile_report, db_chaos_object):
    # сбор статистики сборки сети
    net_compilation_percent_steps = [10, 20, 30, 40, 50, 60, 75, 90, 95, 96, 97, 98, 99, 99.5, 99.9, 100]
    net_compilation_time_points = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    compilation_percent_current_step = 0
    compilation_time_current_step = 0
    elapsed_mins = 0
    start_time = timezone.localtime()
    net_compile_limit_mins = net_compile_report.net_compile_limit_mins
    net_compile_success_percent = net_compile_report.success_percent
    max_net_compile_percent = 0.0

    while True:
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f'Получение новых данных c {db_chaos_object.ip} о cборке сети!')

        current_chaos_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        current_time = timezone.localtime()
        elapsed_time = utils.get_time_delta(current_time,
                                            net_compile_report.create_date_time,
                                            "{hours}:{minutes}:{seconds}")

        if net_compile_report.metric_report:
            add_current_statistic_to_db(db_chaos_object,
                                        current_chaos_statistic_data,
                                        metric_report=net_compile_report.metric_report)
        if current_chaos_statistic_data is None:
            time.sleep(5)
            continue

        net_compilation_percent = get_net_compilation_percent(current_chaos_statistic_data,
                                                              net_compile_report.fact_total_esl)

        if net_compilation_percent > max_net_compile_percent:
            max_net_compile_percent = net_compilation_percent

        print(f'Прошло минут с начала сборки: {elapsed_mins} '
              f'Ценников онлайн: {current_chaos_statistic_data.online_esl} '
              f'Предельное время: {net_compile_limit_mins} '
              f'Текущий % сборки сети: {net_compilation_percent} '
              f'Максимальный % сборки: {max_net_compile_percent} '
              f'Шаг % сборки сети {net_compilation_percent_steps[compilation_percent_current_step]} ')

        if elapsed_mins >= net_compilation_time_points[compilation_time_current_step] \
                and compilation_time_current_step <= len(net_compilation_time_points)-1:
            set_db_object_attribute(net_compile_report,
                                    f't{net_compilation_percent_steps[compilation_time_current_step]}',
                                    current_chaos_statistic_data.get_true_net_compilation_percent())
            compilation_time_current_step += 1

        if max_net_compile_percent >= net_compilation_percent_steps[compilation_percent_current_step]:
            add_net_compilation_statistics_to_db(db_chaos_object,
                                                 net_compile_report,
                                                 current_chaos_statistic_data,
                                                 net_compilation_percent_steps[compilation_percent_current_step],
                                                 elapsed_time)
            set_db_object_attribute(net_compile_report,
                                    f'p{net_compilation_percent_steps[compilation_percent_current_step]}',
                                    elapsed_time)

            print(f'{time_now} Добавлены данные сборки сети. Время:{current_time} Разница: {elapsed_time}', )
            compilation_percent_current_step += 1

        if elapsed_mins > net_compile_limit_mins:
            if max_net_compile_percent >= net_compile_success_percent:
                save_net_compilation_final_status_and_data(net_compile_report, 'OK', max_net_compile_percent)
                return True
            else:
                status = f'Превышено предельное время сборки сети: {net_compile_limit_mins} мин.'
                save_net_compilation_final_status_and_data(net_compile_report, status, max_net_compile_percent)
                return 2

        compilation_percent_last_step = len(net_compilation_percent_steps) - 1
        if max_net_compile_percent == 100 or compilation_percent_current_step >= compilation_percent_last_step:
            net_compile_report.p100 = elapsed_time
            net_compile_report.save()
            save_net_compilation_final_status_and_data(net_compile_report, 'OK', max_net_compile_percent)
            break

        elapsed_mins = (timezone.localtime() - start_time).total_seconds() / 60
        time.sleep(25)
    return True


def draw_images_init(chaos_credentials, db_draw_imgs_object):
    start_storesvc_service(chaos_credentials)
    time.sleep(5)
    if not reset_send_queue(chaos_credentials['ip']):
        status = f'FAIL: 'f'Не удалось сбросить очередь отрисовки перед запуском отрисовки'
        db_draw_imgs_object.status = status
        db_draw_imgs_object.task_id = ''
        db_draw_imgs_object.date_time_finish = timezone.localtime()
        db_draw_imgs_object.save()
        return False
    start_drawing_images(chaos_credentials, db_draw_imgs_object.color)
    time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    print(f'{time_now} Отправка команды на отрисовку...')
    time.sleep(60)
    return True


def draw_images_get_statistics(db_draw_imgs_object, db_chaos_object):
    drawed_percent_points = [10, 20, 30, 40, 50, 60, 75, 90, 95, 96, 97, 98, 99, 99.5, 99.9, 100]
    drawed_time_points = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    drawed_time_points_last_step = len(drawed_time_points) - 1
    start_time = timezone.localtime()
    elapsed_mins = 0
    drawed_percent_current_step = 0
    drawed_time_current_step = 0
    max_drawed_images_percent = 0.0
    while True:
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f'{time_now} Получение новых данных c {db_chaos_object.ip} об отрисовке ценников...')
        current_chaos_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        fact_total_esl = db_draw_imgs_object.fact_total_esl
        current_time = timezone.localtime()
        elapsed_time = utils.get_time_delta(current_time,
                                            db_draw_imgs_object.create_date_time,
                                            "{hours}:{minutes}:{seconds}")

        drawed_images_percent = get_drawed_images_percent(current_chaos_statistic_data, fact_total_esl)

        if drawed_images_percent > max_drawed_images_percent:
            max_drawed_images_percent = drawed_images_percent

        if elapsed_mins > db_draw_imgs_object.draw_imgs_limit_mins:
            status = f'FAIL: 'f'Превышено предельное время отрисовки: {db_draw_imgs_object.draw_imgs_limit_mins} мин.'
            save_draw_imgs_final_status_and_data(
                db_draw_imgs_object,
                current_chaos_statistic_data,
                status)
            return 2

        add_current_statistic_to_db(db_chaos_object,
                                    current_chaos_statistic_data,
                                    metric_report=db_draw_imgs_object.metric_report)
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f'{time_now} Текущий процент отрисовки: '
              f'{drawed_images_percent} '
              f'Отрисовано: {current_chaos_statistic_data.images_succeeded} '
              f'Процент шага: {drawed_percent_points[drawed_percent_current_step]}')

        if drawed_time_current_step <= drawed_time_points_last_step:
            if elapsed_mins >= drawed_time_points[drawed_time_current_step]:
                set_db_object_attribute(db_draw_imgs_object,
                                        f't{drawed_time_points[drawed_time_current_step]}',
                                        current_chaos_statistic_data.get_drawed_images_percent())
                drawed_time_current_step += 1

        if max_drawed_images_percent >= drawed_percent_points[drawed_percent_current_step]:
            add_draw_images_statistics_to_db(db_chaos_object,
                                             db_draw_imgs_object,
                                             current_chaos_statistic_data,
                                             drawed_percent_points[drawed_percent_current_step],
                                             elapsed_time)
            set_db_object_attribute(db_draw_imgs_object,
                                    f'p{drawed_percent_points[drawed_percent_current_step]}',
                                    elapsed_time)
            print(f'{time_now} Добавлены новые метрики. Время: {current_time} Разница: {elapsed_time}', )
            drawed_percent_current_step += 1

        drawed_percent_last_step = len(drawed_percent_points) - 1
        if max_drawed_images_percent == 100 or drawed_percent_current_step > drawed_percent_last_step:
            db_draw_imgs_object.p100 = elapsed_time
            db_draw_imgs_object.save()
            save_draw_imgs_final_status_and_data(db_draw_imgs_object, current_chaos_statistic_data, 'OK')
            break

        elapsed_mins = (timezone.localtime() - start_time).total_seconds() / 60
        time.sleep(25)
    return True


def draw_images_init_sum(chaos, db_draw_imgs_object, chaos_credentials):
    def get_remote_dir_files_list(device_credentials, remote_dir):
        print(f"INFO: получение списка файлов на устройстве {chaos_credentials['ip']}...")
        files_list_command = f"ls -p {remote_dir} | grep -v /"
        response = utils.run_remote_command(device_credentials['ip'],
                                            device_credentials['login'],
                                            device_credentials['password'],
                                            device_credentials['port'], files_list_command)
        if not response[0]:
            return []
        remote_device_files_list = response[0].split('\n')
        print(f"INFO: получен список файлов на устройстве {device_credentials['ip']}...")
        return remote_device_files_list

    def check_exist_files_by_name(file_names_list, search_name):
        find_files = []
        for file_name in file_names_list:
            find_file = file_name.find(search_name)
            if find_file != -1:
                find_files.append(file_name)
        return find_files

    def remove_files_on_host_by_filename(device_credentials, remote_dir_path, files_list):
        print(f"INFO: ининиация удаления файлов на устройстве {device_credentials['ip']}")
        try:
            for file_name in files_list:
                command = f'echo {chaos.password}|sudo -S sudo rm {remote_dir_path + file_name}'
                utils.run_remote_command(device_credentials['ip'],
                                         device_credentials['login'],
                                         device_credentials['password'],
                                         device_credentials['port'], command)
            return True
        except Exception as error:
            print('Что-то пошло не так в процессе удаления dat-файлов')
            print(error)
            return False

    def make_flg_on_remote_host(device_credentials, remote_dir_path, file_name):
        path_to_flg_file = remote_dir_path + file_name + '.flg'
        command = f"echo {device_credentials['password']}|sudo -S sudo touch {path_to_flg_file}"
        try:
            utils.run_remote_command(device_credentials['ip'],
                                     device_credentials['login'],
                                     device_credentials['password'],
                                     device_credentials['port'], command)
            print(f"INFO: успешное создание flg-файла на устройства {device_credentials['ip']}")
            return True
        except Exception as error:
            print(f"INFO: Не удалось создать flg-файла на устройстве {device_credentials['ip']}")
            print(error)
            return False

    remote_directory = '/var/Componentality/storesvc/qpstore/export_magnit/'
    dat_file_name = chaos.dat_file.name
    dat_file_name_wo_expansion = dat_file_name.split('.')[0]
    local_dat_file_dir = os.path.join(BASE_DIR, MEDIA_ROOT)
    local_dat_file_full_path = local_dat_file_dir + chaos.dat_file.name
    local_dat_new_file_path = f'{local_dat_file_dir}{dat_file_name_wo_expansion}_tmp.dat'
    remote_dat_file_path = remote_directory + dat_file_name

    start_storesvc_service(chaos_credentials)
    time.sleep(5)

    if not reset_send_queue(chaos.ip):
        status = f'FAIL: 'f'Не удалось сбросить очередь отрисовки перед запуском отрисовки'
        db_draw_imgs_object.status = status
        db_draw_imgs_object.task_id = ''
        db_draw_imgs_object.date_time_finish = timezone.localtime()
        db_draw_imgs_object.save()
        return False

    if not dat_file_change_prices(local_dat_file_full_path, local_dat_new_file_path):
        return False

    files_list = get_remote_dir_files_list(chaos_credentials, remote_directory)
    filtered_files = check_exist_files_by_name(files_list, dat_file_name_wo_expansion)

    if not remove_files_on_host_by_filename(chaos_credentials, remote_directory, filtered_files):
        return False

    if not utils.copy_file_over_ssh(chaos_credentials['ip'],
                                    chaos_credentials['login'],
                                    chaos_credentials['password'],
                                    chaos_credentials['port'],
                                    local_dat_new_file_path, remote_dat_file_path):
        return False

    os.remove(local_dat_new_file_path)
    time.sleep(5)

    if not make_flg_on_remote_host(chaos_credentials, remote_directory, dat_file_name_wo_expansion):
        return False
    return True


def get_chaos_configuration(chaos_pk, report_object):
    def get_version(version_num):
        version_exist = Version.objects.filter(version_num=version_num)
        if version_exist:
            return version_exist[0]
        else:
            version = Version.objects.create(version_num=version_num)
            version.save()
            return version

    chaos = Chaos.objects.get(pk=chaos_pk)
    chaos_info = ChaosConfigurationInfo(chaos.ip)
    current_statistics = ChaosStatisctic(chaos.ip)

    try:
        release_version = get_version(chaos_info.release_version)
        configuration = Configuration.objects.create(chaos=chaos,
                                                     netcompile_report=None,
                                                     metric_report=None,
                                                     drawimgs_report=None,
                                                     version_num=release_version,
                                                     shields_num=chaos.shields_num,
                                                     hardware_config=chaos.hardware_config,
                                                     total_esl=current_statistics.total_esl,
                                                     dd_nums=chaos_info.distributing_device_num,
                                                     dd_configuration='',
                                                     dd_dongles_num=chaos_info.dongles_num,
                                                     version_sum=chaos_info.version_sum,
                                                     version_chaos=chaos_info.release_version,
                                                     chaos_configuration=chaos_info.chaos_config,
                                                     tree_floor_num=chaos_info.tree_floor_num,
                                                     version_driver=chaos_info.release_version,
                                                     version_esl_firmware=chaos_info.sw_versions,
                                                     version_esl_hw=chaos_info.hw_versions,
                                                     version_dongles_hw=chaos_info.dongles_versions,
                                                     )
        if type(report_object) == MetricReport:
            configuration.metric_report = report_object
        if type(report_object) == NetCompileReport:
            configuration.netcompile_report = report_object
        if type(report_object) == DrawImgsReport:
            configuration.drawimgs_report = report_object
        configuration.save()
        print(f'Конфигурация для {chaos.name}({chaos.ip}) успешно создана')
        report_object.config = configuration
        report_object.save()
        return configuration
    except IntegrityError:
        print(f'Не удалось связать конфигурацию с отчетом: указанный ID отчета уже связан с другой конфигурацией')
        return None
    except Exception as error:
        print(f'Не удалось создать конфигурацию для {chaos.name}({chaos.ip}). error: {error}')
        return None


def save_report_voltage_average(report_object):
    report_start_time = report_object.create_date_time
    report_finish_time = report_object.date_time_finish
    if report_finish_time is None:
        report_finish_time = timezone.localtime()
    statistics = Statistic.objects.filter(chaos_id=report_object.chaos.id).filter(
        date_time__range=(report_start_time, report_finish_time))
    voltage_average = statistics.aggregate(Avg('voltage_average'))['voltage_average__avg']
    if voltage_average is not None:
        voltage_average = float('{:.3f}'.format(voltage_average))
    else:
        voltage_average = None
    report_object.voltage_average = voltage_average
    report_object.save()
    return


if __name__ == '__main__':
    pass
