import time
import ast
from conf.celery import app
from django.utils import timezone
from main.chaos_utils import Utils as utils
from main.chaos_utils import ChaosStatisctic
from main.models import NetCompileReport, DrawImgsReport, Chaos, MetricReport
from main.tasks.tasks_tools import add_current_statistic_to_db, \
    add_net_compilation_statistics_to_db, set_db_object_attribute, get_default_devices, get_ips_by_names, \
    reboot_devices_list, check_all_alive, start_drawing_images, add_draw_images_statistics_to_db, \
    get_drawed_images_percent, save_draw_imgs_final_status_and_data, save_net_compilation_final_status_and_data,\
    get_net_compilation_percent, start_chaos_webcore, stop_chaos_webcore, reset_send_queue, get_chaos_config


@app.task(autoretry_for=(Exception,))
def get_current_stats():
    chaoses = Chaos.objects.all()
    for chaos in chaoses:
        statistic = ChaosStatisctic(ip=chaos.ip)
        if statistic.text != 'None':
            add_current_statistic_to_db(chaos, statistic)
            chaos.status = 'OK'
            chaos.esl_total = statistic.total_esl
            chaos.images_succeeded = statistic.images_succeeded
            chaos.net_percent = f'{statistic.get_true_net_compilation_percent():.2f}'
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
    net_compilation_percent = 0

    # --------перезагрузка устройств------
    server_names_ports = get_default_devices(chaos_credentials)
    if not server_names_ports:
        status = f'FAIL: Не удалось получить DEFAULT_RSERVERS c устройства {server_ssh_address}'
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
        status = 'FAIL: Одного или несколько устройство недоступно после перезагрузки'
        save_net_compilation_final_status_and_data(net_compile_report, status, net_compilation_percent)
        return False
    # if not reboot_devices_list([f"{chaos_credentials['ip']}:19871"], chaos_credentials):
    #     status = 'FAIL: Не удалось инициировать перезагрузку chaos'
    #     save_net_compilation_final_status_and_data(net_compile_report, status, net_compilation_percent)
    #     return False
    # print('OK! инициирована перезагрузка устройств!')
    time.sleep(60)
    start_chaos_webcore(chaos_credentials)

    # --------сборка сети------
    net_compilation_percent_steps = [10, 20, 30, 40, 50, 60, 75, 90, 95, 96, 97, 98, 99, 99.5, 99.9, 100]
    net_compilation_time_points = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    compilation_percent_current_step = 0
    compilation_time_current_step = 0
    elapsed_mins = 0
    start_time = timezone.localtime(timezone.now())
    net_compile_limit_mins = net_compile_report.net_compile_limit_mins

    while True:
        print(f'Получение новых данных c {db_chaos_object.ip} о cборке сети!')

        current_chaos_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        current_time = timezone.localtime(timezone.now())
        elapsed_time = utils.get_time_delta(current_time,
                                            net_compile_report.create_date_time,
                                            "{hours}:{minutes}:{seconds}")

        print(f'Прошло минут с начала сборки: {elapsed_mins} Предельное время: {net_compile_limit_mins}')

        if net_compile_report.metric_report:
            add_current_statistic_to_db(db_chaos_object,
                                        current_chaos_statistic_data,
                                        metric_report=net_compile_report.metric_report)
        if current_chaos_statistic_data is None:
            time.sleep(5)
            continue

        net_compilation_percent = get_net_compilation_percent(current_chaos_statistic_data,
                                                              net_compile_report.fact_total_esl)

        if elapsed_mins >= net_compilation_time_points[compilation_time_current_step]:
            set_db_object_attribute(net_compile_report,
                                    f't{net_compilation_percent_steps[compilation_time_current_step]}',
                                    current_chaos_statistic_data.get_true_net_compilation_percent())
            compilation_time_current_step += 1

        if net_compilation_percent >= net_compilation_percent_steps[compilation_percent_current_step]:
            add_net_compilation_statistics_to_db(db_chaos_object,
                                                 net_compile_report,
                                                 current_chaos_statistic_data,
                                                 net_compilation_percent_steps[compilation_percent_current_step],
                                                 elapsed_time)
            set_db_object_attribute(net_compile_report,
                                    f'p{net_compilation_percent_steps[compilation_percent_current_step]}',
                                    elapsed_time)
            # net_compile_report.save()
            print(f'Добавлены данные сборки сети. Время:{current_time} Разница: {elapsed_time}', )
            compilation_percent_current_step += 1

        if elapsed_mins > net_compile_limit_mins:
            status = f'Превышено предельное время сборки сети: {net_compile_limit_mins} мин.'
            save_net_compilation_final_status_and_data(net_compile_report, status, net_compilation_percent)
            return 2

        compilation_percent_last_step = len(net_compilation_percent_steps) - 1
        if net_compilation_percent == 100 or compilation_percent_current_step >= compilation_percent_last_step:
            net_compile_report.p100 = elapsed_time
            net_compile_report.save()
            save_net_compilation_final_status_and_data(net_compile_report, 'OK')
            break

        elapsed_mins = (timezone.localtime(timezone.now()) - start_time).total_seconds() / 60
        time.sleep(60)
    return True


@app.task
def drawed_images_report_generate(id_report):
    drawed_percent_points = [10, 20, 30, 40, 50, 60, 75, 90, 95, 96, 97, 98, 99, 99.5, 99.9, 100]
    drawed_time_points = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    db_draw_imgs_object = DrawImgsReport.objects.get(pk=id_report)
    db_chaos_object = Chaos.objects.get(pk=db_draw_imgs_object.chaos_id)
    fact_total_esl = db_draw_imgs_object.fact_total_esl
    chaos_credentials = {'ip': db_chaos_object.ip,
                         'login': db_chaos_object.login,
                         'password': db_chaos_object.password,
                         'port': db_chaos_object.ssh_port
                         }
    start_time = timezone.localtime(timezone.now())
    elapsed_mins = 0
    drawed_percent_current_step = 0
    drawed_time_current_step = 0

    if not reset_send_queue(chaos_credentials['ip']):
        status = f'FAIL: 'f'Не удалось сбросить очередь отрисовки перед запуском отрисовки'
        db_draw_imgs_object.status = status
        db_draw_imgs_object.date_time_finish = timezone.localtime(timezone.now())
        db_draw_imgs_object.save()
        return False
    start_drawing_images(chaos_credentials, db_draw_imgs_object.color)
    print('Отправка команды на отрисовку...')
    time.sleep(60)

    while True:
        print(f'Получение новых данных c {db_chaos_object.ip} об отрисовке ценников...')
        current_chaos_statistic_data = ChaosStatisctic(ip=db_chaos_object.ip)
        drawed_images_percent = get_drawed_images_percent(current_chaos_statistic_data, fact_total_esl)
        current_time = timezone.localtime(timezone.now())
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
              f'Процент шага: {drawed_percent_points[drawed_percent_current_step]}')

        if elapsed_mins >= drawed_time_points[drawed_time_current_step]:
            setattr(db_draw_imgs_object, f't{drawed_time_points[drawed_time_current_step]}',
                    current_chaos_statistic_data.get_drawed_images_percent())

        if drawed_images_percent >= drawed_percent_points[drawed_percent_current_step]:
            add_draw_images_statistics_to_db(db_chaos_object,
                                             db_draw_imgs_object,
                                             current_chaos_statistic_data,
                                             drawed_percent_points[drawed_percent_current_step],
                                             elapsed_time)
            setattr(db_draw_imgs_object, f'p{drawed_percent_points[drawed_percent_current_step]}', elapsed_time)
            # db_draw_imgs_object.save()
            print(f'Добавлены новые метрики. Время: {current_time} Разница: {elapsed_time}', )
            drawed_percent_current_step += 1

        drawed_percent_last_step = len(drawed_percent_points) - 1
        if drawed_images_percent == 100 or drawed_percent_current_step > drawed_percent_last_step:
            db_draw_imgs_object.p100 = elapsed_time
            db_draw_imgs_object.save()
            save_draw_imgs_final_status_and_data(db_draw_imgs_object, current_chaos_statistic_data, 'OK')
            break

        elapsed_mins = (timezone.localtime(timezone.now()) - start_time).total_seconds() / 60
        time.sleep(60)
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
                color=metric_report.color,
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
    metric_report.date_time_finish = timezone.localtime(timezone.now())
    metric_report.save()
    return True


@app.task
def compire_chaos_configs():
    chaoses = Chaos.objects.all()
    for chaos in chaoses:
        errors = 0
        warnings = 0
        print(f'Сравнение конфигурационных файлов для {chaos.name}({chaos.ip})')
        compired_config = ''
        chaos_credentials = {'ip': chaos.ip,
                             'login': chaos.login,
                             'password': chaos.password,
                             'port': chaos.ssh_port
                             }
        current_config = get_chaos_config(chaos_credentials)
        if current_config is None:
            continue
        if not chaos.config:
            chaos.config = current_config
            chaos.save()
        reference_config = ast.literal_eval(str(chaos.config))
        monitored_params = chaos.monitoring_config_params
        for param in reference_config:
            config_line = f'{param}: {reference_config[param]} ({current_config[param]})'
            if monitored_params is not None:
                if param in monitored_params:
                    config_line = f'<b>{param}</b>: {reference_config[param]} ({current_config[param]})'
            if reference_config[param] != current_config[param] and param in monitored_params:
                config_line = f' <span class="badge badge-pill badge-danger">ERR!</span> {config_line}'
                errors += 1
            elif reference_config[param] != current_config[param]:
                config_line = f' <span class="badge badge-pill badge-warning">WARN</span> {config_line}'
                warnings += 1
            else:
                config_line = f' <span class="badge badge-pill badge-success">GOOD</span> {config_line}'
            compired_config += config_line + '<br/>'
        chaos.compired_config_errs = errors
        chaos.compired_config_warns = warnings
        chaos.compired_config = compired_config
        chaos.compired_config_date = timezone.localtime(timezone.now())
        chaos.save()
