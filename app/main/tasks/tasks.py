import time
import ast
from conf.celery import app
from django.utils import timezone
from datetime import datetime
from main.chaos_utils import ChaosStatisctic
from main.models import NetCompileReport, DrawImgsReport, Chaos, MetricReport
from main.tasks.tasks_tools import add_current_statistic_to_db, set_db_object_attribute, get_chaos_config,\
    net_compilation_init, net_compilation_get_statistics, draw_images_init, draw_images_get_statistics,\
    create_net_compilation_report, create_draw_imgs_report, draw_images_init_sum


@app.task(autoretry_for=(Exception,))
def run_get_current_stats_task():
    chaoses = Chaos.objects.all()
    for chaos in chaoses:
        statistic = ChaosStatisctic(ip=chaos.ip)
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        if statistic.text != 'None':
            add_current_statistic_to_db(chaos, statistic)
            chaos.status = 'OK'
            chaos.esl_total = statistic.total_esl
            chaos.images_succeeded = statistic.images_succeeded
            chaos.net_percent = f'{statistic.get_true_net_compilation_percent():.2f}'
            chaos.draw_percent = statistic.get_drawed_images_percent()
            chaos.date_time_update = timezone.localtime()
            chaos.save()
            # print(f'{time_now} {chaos.ip} is ONLINE. add stats to DB')
        else:
            # print(f'{time_now} {chaos.ip} is OFFLINE. add chaos status to DB')
            set_db_object_attribute(chaos, 'status', 'OFFLINE')


@app.task
def run_net_compilation_task(id_report):
    net_compile_report = NetCompileReport.objects.get(pk=id_report)
    db_chaos_object = Chaos.objects.get(pk=net_compile_report.chaos_id)
    chaos_credentials = {'ip': db_chaos_object.ip,
                         'login': db_chaos_object.login,
                         'password': db_chaos_object.password,
                         'port': db_chaos_object.ssh_port
                         }
    net_compilation_init_result = net_compilation_init(chaos_credentials, net_compile_report)
    if net_compilation_init_result is False:
        return net_compilation_init_result
    net_compilation_result = net_compilation_get_statistics(net_compile_report, db_chaos_object)
    return net_compilation_result


@app.task
def run_drawed_images_report_generate_task(id_report):
    db_draw_imgs_object = DrawImgsReport.objects.get(pk=id_report)
    db_chaos_object = Chaos.objects.get(pk=db_draw_imgs_object.chaos_id)
    chaos_credentials = {'ip': db_chaos_object.ip,
                         'login': db_chaos_object.login,
                         'password': db_chaos_object.password,
                         'port': db_chaos_object.ssh_port
                         }
    if db_draw_imgs_object.draw_imgs_type == 'highlight':
        draw_images_init_result = draw_images_init(chaos_credentials, db_draw_imgs_object)
    elif db_draw_imgs_object.draw_imgs_type == 'sum':
        draw_images_init_result = draw_images_init_sum(db_chaos_object)
    else:
        return False
    if draw_images_init_result is False:
        return draw_images_init_result
    draw_images_result = draw_images_get_statistics(db_draw_imgs_object, db_chaos_object)
    return draw_images_result


@app.task
def run_all_metrics_report_generate_task(id_report):
    metric_report = MetricReport.objects.get(pk=id_report)
    net_compiles_amount = metric_report.net_compile_amount
    draw_imgs_amount = metric_report.draw_imgs_amount

    while net_compiles_amount != 0:
        net_compilation_report = create_net_compilation_report(metric_report)
        result = run_net_compilation_task(net_compilation_report.id)
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        if result == 2:
            print(f'{time_now} Превышено предельное время cборки сети.')
            net_compiles_amount -= 1
            continue
        if result == 1:
            print(f'{time_now} Успешная сборка сети')
            net_compiles_amount -= 1

        draw_imgs_count = draw_imgs_amount
        while draw_imgs_count != 0:
            draw_imgs_report = create_draw_imgs_report(metric_report)
            result = run_drawed_images_report_generate_task(draw_imgs_report.id)
            time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
            if result == 2:
                print(f'{time_now} Превышено предельное время отрисовки.')
                draw_imgs_count -= 1
            elif result == 1:
                print(f'{datetime} Успешная отрисовка')
                draw_imgs_count -= 1
            elif result == 3:
                print(f'{datetime} Ошибка в процессе выполнения скрипта')
            else:
                break
    metric_report.date_time_finish = timezone.localtime()
    metric_report.status = 'OK'
    metric_report.save()
    return True


@app.task
def run_compire_chaos_configs_task():
    chaoses = Chaos.objects.all()
    for chaos in chaoses:
        time_now = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        errors = 0
        warnings = 0
        print(f'{time_now} Сравнение конфигурационных файлов для {chaos.name}({chaos.ip})')
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
        chaos.compired_config_date = timezone.localtime()
        chaos.save()
