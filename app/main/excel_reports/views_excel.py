from main.models import Statistic,  MetricReport, Chaos, DrawImgsReport,\
    NetCompileReport, DrawImgsStat, NetCompilationStat, Configuration
from main.excel_reports.excel_tools import create_excel_cheet, create_excel_cheet_for_stats, create_excel_net_draw_cheet,\
    add_one_cell_data
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
from openpyxl import Workbook
from main.excel_reports.excel_report_fields import net_compile_short_report_draw_fields,\
    draw_imgs_stats_short_report_draw_fields, net_compile_reports_draw_fields, draw_imgs_reports_draw_fields,\
    draw_imgs_stat_fields, net_compile_stat_fields, metrics_report_common_statistic_draw_fields,\
    net_compile_fields_common_report, draw_imgs_fields_common_report, net_compile_fields_common_extended_report,\
    draw_imgs_fields_common_extended_report, chaos_configuration_fields


def metric_report_export_to_xlsx(request, metric_report_id):
    """
    Генерация excel-отчета со страницы снятия общих метрик /metrics/<report_ID>/
    :param request:
    :param metric_report_id:
    :return:
    """
    metrics_report = MetricReport.objects.get(pk=metric_report_id)

    report_start_time = metrics_report.create_date_time
    report_finish_time = metrics_report.date_time_finish
    if report_finish_time is None:
        report_finish_time = timezone.localtime()

    net_compile_reports = NetCompileReport.objects.filter(metric_report=metrics_report)
    draw_imgs_reports = DrawImgsReport.objects.filter(metric_report=metrics_report)
    metrics_report_common_statistic = Statistic.objects.filter(metric_report=metrics_report).filter(
        date_time__range=(report_start_time, report_finish_time)).order_by('date_time')
    configuration = Configuration.objects.filter(metric_report=metrics_report)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-metric_report_{chaos_name}.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
        chaos_name=metrics_report.chaos.name
    )
    draw_imgs_amount = metrics_report.draw_imgs_amount
    workbook = Workbook()
    workbook = create_excel_cheet_for_stats(workbook, draw_imgs_reports, DrawImgsStat, draw_imgs_stat_fields)
    workbook = create_excel_cheet_for_stats(workbook, net_compile_reports, NetCompilationStat, net_compile_stat_fields)
    workbook = create_excel_cheet(workbook, net_compile_reports, net_compile_reports_draw_fields, vertical=True)
    workbook = create_excel_cheet(workbook, draw_imgs_reports, draw_imgs_reports_draw_fields, vertical=True)
    workbook = create_excel_cheet(workbook,
                                  metrics_report_common_statistic,
                                  metrics_report_common_statistic_draw_fields)
    workbook = create_excel_net_draw_cheet(workbook,
                                           net_compile_reports, net_compile_fields_common_extended_report,
                                           draw_imgs_reports, draw_imgs_fields_common_extended_report,
                                           draw_imgs_amount,
                                           'Сводный отчет (расширенный)',
                                           vertical=True)
    workbook = create_excel_net_draw_cheet(workbook,
                                           net_compile_reports, net_compile_fields_common_report,
                                           draw_imgs_reports, draw_imgs_fields_common_report,
                                           draw_imgs_amount,
                                           'Сводный отчет',
                                           vertical=True)
    worksheet_name = 'Сводный отчет'
    merge_cell_num = metrics_report.net_compile_amount * metrics_report.draw_imgs_amount
    voltage_average = metrics_report.voltage_average

    workbook = add_one_cell_data(workbook, worksheet_name, 'Среднее значение потребления (общее), mA', voltage_average,
                                 merge=True, merge_num=merge_cell_num, vertical=True)

    workbook = create_excel_cheet(workbook, configuration, chaos_configuration_fields, vertical=True)
    workbook.save(response)
    return response


def chaos_stats_export_to_xlsx(request, chaos_id):
    """
    Генерация excel-отчета со страницы (chaoses/<chaos_ID>/stats) по всем сборкам\отрисовкам
    :param request:
    :param chaos_id:
    :return:
    """
    chaos = Chaos.objects.get(pk=chaos_id)
    net_compile_reports = NetCompileReport.objects.filter(chaos=chaos).order_by('-create_date_time')
    draw_imgs_reports = DrawImgsReport.objects.filter(chaos=chaos).order_by('-create_date_time')
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-nets_draws_report_{chaos_name}.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
        chaos_name=chaos.name
    )

    workbook = Workbook()
    workbook = create_excel_cheet(workbook, net_compile_reports, net_compile_short_report_draw_fields)
    workbook = create_excel_cheet(workbook, draw_imgs_reports, draw_imgs_stats_short_report_draw_fields)
    workbook.save(response)
    return response


def draw_imgs_report_export_to_xlsx(request, draw_imgs_report_id):
    """
    Генерация excel-отчета со страницы (drawed/<draw_imgs_report_id>) отрисовки ценников
    :param request:
    :param draw_imgs_report_id:
    :return:
    """
    current_time = timezone.localtime()
    draw_imgs_report = DrawImgsReport.objects.filter(pk=draw_imgs_report_id)
    chaos = draw_imgs_report[0].chaos
    configuration = Configuration.objects.filter(drawimgs_report=draw_imgs_report[0])
    draw_imgs_report_start_time = draw_imgs_report[0].create_date_time
    draw_imgs_report_end_time = draw_imgs_report[0].date_time_finish
    if draw_imgs_report_end_time is None:
        draw_imgs_report_end_time = current_time
    statistics = Statistic.objects.filter(chaos=chaos).\
        filter(date_time__range=[draw_imgs_report_start_time, draw_imgs_report_end_time]).order_by('date_time')
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-draw_imgs_report_{chaos_name}.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
        chaos_name=chaos.name
    )

    workbook = Workbook()
    workbook = create_excel_cheet_for_stats(workbook, draw_imgs_report, DrawImgsStat, draw_imgs_stat_fields)
    workbook = create_excel_cheet(workbook, draw_imgs_report, draw_imgs_stats_short_report_draw_fields, vertical=True)
    workbook = create_excel_cheet(workbook,
                                  statistics,
                                  metrics_report_common_statistic_draw_fields)
    workbook = create_excel_cheet(workbook, configuration, chaos_configuration_fields, vertical=True)
    workbook.save(response)
    return response


def net_compile_report_export_to_xlsx(request, net_compile_id):
    """
    Генерация excel-отчета со страницы (netcompiles/<net_compile_id>) сборки сети
    :param request:
    :param net_compile_id:
    :return:
    """
    current_time = timezone.localtime()
    net_compile_report = NetCompileReport.objects.filter(pk=net_compile_id)
    chaos = net_compile_report[0].chaos
    configuration = Configuration.objects.filter(netcompile_report=net_compile_report[0])
    net_compile_start_time = net_compile_report[0].create_date_time
    net_compile_end_time = net_compile_report[0].date_time_finish
    if net_compile_end_time is None:
        net_compile_end_time = current_time
    statistics = Statistic.objects.filter(chaos=chaos).\
        filter(date_time__range=[net_compile_start_time, net_compile_end_time]).order_by('date_time')
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-net_compile_report_{chaos_name}.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
        chaos_name=chaos.name
    )

    workbook = Workbook()
    workbook = create_excel_cheet_for_stats(workbook, net_compile_report, NetCompilationStat, net_compile_stat_fields)
    workbook = create_excel_cheet(workbook, net_compile_report, net_compile_short_report_draw_fields, vertical=True)
    workbook = create_excel_cheet(workbook,
                                  statistics,
                                  metrics_report_common_statistic_draw_fields)
    workbook = create_excel_cheet(workbook, configuration, chaos_configuration_fields, vertical=True)
    workbook.save(response)
    return response
