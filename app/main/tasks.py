import time
from datetime import datetime
from conf.celery import app
from main.chaos_utils import Utils as utils
from main.chaos_utils import ChaosStatisctic
from main.models import NetCompileReport, DrawImgsReport, Chaos, MetricReport
from main.tasks_tools import add_current_statistic_to_db, \
    add_net_compilation_statistics_to_db, set_db_object_attribute, get_default_devices, get_ips_by_names, \
    reboot_devices_list, check_all_alive, start_drawing_images, add_draw_images_statistics_to_db, \
    get_drawed_images_percent, save_draw_imgs_final_status_and_data, save_net_compilation_final_status_and_data,\
    get_net_compilation_percernt


@app.task
def get_current_stats():
    chaoses = Chaos.objects.all()
    for chaos in chaoses:
        statistic = ChaosStatisctic(ip=chaos.ip)
        if statistic.text != 'None':
            add_current_statistic_to_db(chaos, statistic)
            chaos.status = 'OK'
            chaos.esl_total = statistic.total_esl
            chaos.images_succeeded = statistic.images_succeeded
            chaos.net_percent = statistic.get_net_compilation_percent()
            chaos.draw_percent = statistic.get_drawed_images_percent()
            chaos.save()
            print(f'{chaos.ip} is ONLINE. add stats to DB')
        else:
            print(f'{chaos.ip} is OFFLINE. add chaos status to DB')
            set_db_object_attribute(chaos, 'status', 'OFFLINE')


@app.task
def net_compilation(id_report):
    net_compile_report = NetCompileReport.objects.get(pk=id_report)
    db_chaos_object = Chaos.objects.get(pk=net_compile_report.chaos_id)
    server_ssh_address = db_chaos_object.ip
    chaos_credentials = {'ip': db_chaos_object.ip,
                         'login': db_chaos_object.login,
                         'password': db_chaos_object.password,
                         'port': db_chaos_object.ssh_port
                         }

    # --------перезагрузка устройств------
    server_names_ports = get_default_devices(chaos_credentials)
    if server_names_ports is None:
        status = f'FAIL: Не удалось получить DEFAULT_RSERVERS c устройства {server_ssh_address}'
        save_net_compilation_final_status_and_data(net_compile_report, status)
        return False
    servers_ips_ports = get_ips_by_names(server_names_ports, chaos_credentials)
    if not reboot_devices_list(servers_ips_ports, chaos_credentials):
        status = 'FAIL: Не удалось инициировать перезагрузку одного или нескольких устройств'
        save_net_compilation_final_status_and_data(net_compile_report, status)
        return False
    print('OK! инициирована перезагрузка устройства!')
    time.sleep(30)
    if not check_all_alive(servers_ips_ports, chaos_credentials['ip'], 5):
        status = 'FAIL: Одного или несколько устройство недоступно после перезагрузки'
        save_net_compilation_final_status_and_data(net_compile_report, status)
        return False
    time.sleep(30)

    # --------сборка сети------
    net_compilation_percernt_steps = [10, 20, 30, 40, 50, 60, 75, 90, 95, 96, 97, 98, 99, 100]
    last_step = len(net_compilation_percernt_steps)-1
    current_step = 0
    elapsed_mins = 0
    start_time = datetime.now()
    net_compile_limit_mins = net_compile_report.net_compile_limit_mins

    while True:
        print(f'Получение новых данных c {db_chaos_object.ip} о cборке сети!')

        current_chaos_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        current_time = utils.get_time_now()
        elapsed_time = utils.get_time_delta(current_time,
                                            net_compile_report.create_date_time,
                                            "{hours}:{minutes}:{seconds}")

        print(f'Прошло минут с начала сборки: {elapsed_mins} Предельное время: {net_compile_limit_mins}')

        if elapsed_mins > net_compile_limit_mins:
            status = f'Превышено предельное время сборки сети: {net_compile_limit_mins} мин.'
            save_net_compilation_final_status_and_data(net_compile_report, status)
            return 2

        if net_compile_report.metric_report:
            add_current_statistic_to_db(db_chaos_object,
                                        current_chaos_statistic_data,
                                        metric_report=net_compile_report.metric_report)
        if current_chaos_statistic_data is None:
            time.sleep(5)
            continue

        net_compilation_percernt = get_net_compilation_percernt(current_chaos_statistic_data,
                                                                net_compile_report.fact_total_esl)

        if net_compilation_percernt >= net_compilation_percernt_steps[current_step]:
            add_net_compilation_statistics_to_db(db_chaos_object,
                                                 net_compile_report,
                                                 current_chaos_statistic_data,
                                                 net_compilation_percernt,
                                                 elapsed_time)
            set_db_object_attribute(net_compile_report,
                                    f'p{net_compilation_percernt_steps[current_step]}',
                                    elapsed_time)
            net_compile_report.save()
            print(f'Добавлены данные сборки сети. Время:{current_time} Разница: {elapsed_time}', )
            current_step += 1

        if net_compilation_percernt == 100 or current_step > last_step:
            net_compile_report.p100 = elapsed_time
            net_compile_report.save()
            save_net_compilation_final_status_and_data(net_compile_report, 'OK')
            break

        elapsed_mins = (utils.get_time_now() - start_time).total_seconds() / 60
        time.sleep(10)
    return True


@app.task
def drawed_images_report_generate(id_report):
    drawed_percent_points = [10, 20, 30, 40, 50, 60, 75, 90, 95, 96, 97, 98, 99, 100]
    db_draw_imgs_object = DrawImgsReport.objects.get(pk=id_report)
    db_chaos_object = Chaos.objects.get(pk=db_draw_imgs_object.chaos_id)
    fact_total_esl = db_draw_imgs_object.fact_total_esl
    chaos_credentials = {'ip': db_chaos_object.ip,
                         'login': db_chaos_object.login,
                         'password': db_chaos_object.password,
                         'port': db_chaos_object.ssh_port
                         }
    start_time = datetime.now()
    elapsed_mins = 0
    current_step = 0

    start_drawing_images(chaos_credentials)
    print('Отправка команды на отрисовку...')
    time.sleep(120)

    while True:
        print(f'Получение новых данных c {db_chaos_object.ip} об отрисовке ценников...')
        current_chaos_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        drawed_images_percent = get_drawed_images_percent(current_chaos_statistic_data, fact_total_esl)
        current_time = utils.get_time_now()
        elapsed_time = utils.get_time_delta(current_time,
                                            db_draw_imgs_object.create_date_time,
                                            "{hours}:{minutes}:{seconds}")

        # if not connection:
        #     status = f'FAIL: Нет удалось отправить команду на отрисовку {connection}'
        #     save_draw_imgs_final_status_and_data(db_draw_imgs_object, current_chaos_statistic_data, status)
        #     return 0

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

        print(f'Текущий процент отрисовки: '
              f'{drawed_images_percent} '
              f'Отрисовано: {current_chaos_statistic_data.images_succeeded} '
              f'Процент шага: {drawed_percent_points[current_step]}')

        if drawed_images_percent >= drawed_percent_points[current_step]:
            add_draw_images_statistics_to_db(db_chaos_object,
                                             db_draw_imgs_object,
                                             current_chaos_statistic_data,
                                             drawed_percent_points[current_step],
                                             elapsed_time)
            setattr(db_draw_imgs_object, f'p{drawed_percent_points[current_step]}', elapsed_time)
            db_draw_imgs_object.save()
            print(f'Добавлены новые метрики. Время: {current_time} Разница: {elapsed_time}', )
            current_step += 1

        last_step = len(drawed_percent_points) - 1
        if drawed_images_percent == 100 or current_step > last_step:
            db_draw_imgs_object.p100 = elapsed_time
            db_draw_imgs_object.save()
            save_draw_imgs_final_status_and_data(db_draw_imgs_object, current_chaos_statistic_data, 'OK')
            break

        elapsed_mins = (utils.get_time_now() - start_time).total_seconds() / 60
        time.sleep(30)
    return True


@app.task
def all_metrics_report_generate(id_report):
    metric_report = MetricReport.objects.get(pk=id_report)
    chaos = Chaos.objects.get(pk=metric_report.chaos.pk)
    net_compiles_amount = metric_report.net_compile_amount
    draw_imgs_amount = metric_report.draw_imgs_amount

    while net_compiles_amount != 0:
        net_compilation_report = NetCompileReport.objects.create(
            metric_report=metric_report,
            chaos=chaos,
            fact_total_esl=metric_report.fact_total_esl,
            net_compile_limit_mins=metric_report.net_compile_limit_mins,
            net_compile_amount=metric_report.net_compile_amount,
        )
        net_compilation_report.save()
        result = net_compilation(net_compilation_report.id)
        if result == 2:
            print('Превышено предельное время cборки сети.')
            net_compiles_amount -= 1
            continue
        if result == 1:
            print('Успешная сборка сети')
            net_compiles_amount -= 1

        draw_imgs_count = draw_imgs_amount
        while draw_imgs_count != 0:
            draw_imgs_report = DrawImgsReport.objects.create(
                metric_report=metric_report,
                chaos=chaos,
                fact_total_esl=metric_report.fact_total_esl,
                draw_imgs_limit_mins=metric_report.draw_imgs_limit_mins,
                draw_imgs_amount=metric_report.draw_imgs_amount,
            )
            draw_imgs_report.save()
            result = drawed_images_report_generate(draw_imgs_report.id)
            if result == 2:
                print('Превышено предельное время отрисовки.')
                draw_imgs_count -= 1
            elif result == 1:
                print('Успешная отрисовка')
                draw_imgs_count -= 1
            else:
                break
    metric_report.date_time_finish = datetime.now()
    metric_report.save()
    return True
