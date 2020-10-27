from main.models import Statistic,  MetricReport, Chaos, DrawImgsReport,\
    NetCompileReport, DrawImgsStat, NetCompilationStat
from main.excel_reports.excel_tools import create_excel_cheet, create_excel_cheet_for_stats, create_excel_net_draw_cheet
from django.http import HttpResponse
from datetime import datetime
from openpyxl import Workbook


def metric_report_export_to_xlsx(request, metric_report_id):
    """
    Генерация excel-отчета со страницы снятия общих метрик /metrics/<report_ID>/
    :param request:
    :param metric_report_id:
    :return:
    """
    metrics_report = MetricReport.objects.get(pk=metric_report_id)
    net_compile_reports = NetCompileReport.objects.filter(metric_report=metrics_report)
    draw_imgs_reports = DrawImgsReport.objects.filter(metric_report=metrics_report)
    metrics_report_common_statistic = Statistic.objects.filter(metric_report=metrics_report).order_by('date_time')

    net_compile_reports_draw_fields = ['create_date_time', 'status',
                                       'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100',
                                       'fact_total_esl', 'date_time_finish',
                                       ]
    draw_imgs_reports_draw_fields = ['create_date_time', 'status',
                                     'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100', 'fact_total_esl',
                                     'drawed_esl', 'not_drawed_esl', 'date_time_finish'
                                     ]
    draw_imgs_stat_fields = ['percent_step', 'elapsed_time', 'images_succeeded']
    net_compile_stat_fields = ['compilation_percent', 'online_esl', 'elapsed_time']
    metrics_report_common_statistic_draw_fields = [
        'date_time',
        'total_nodes',
        'inaccessible_nodes',
        'total_number_routes',
        'maximum_road_length',
        'average_route_length',
        'accessible_nodes_percent',
        'elapsed_time',
        'total_esl',
        'online_esl',
        'images_in_transit',
        'images_in_draw',
        'images_in_resend_queue',
        'images_succeeded',
        'images_failed',
        'currently_scanning',
        'network_mode',
        'connects',
    ]

    net_compile_fields_common_report = ['create_date_time', 'elapsed_time', 'final_percent', 't60', 'fact_total_esl',
                                        'status',
                                       ]
    draw_imgs_fields_common_report = ['p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p995', 'p999', 'p100',
                                      'not_drawed_esl',
                                     ]
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-metric_report.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
    )
    draw_imgs_amount = metrics_report.draw_imgs_amount
    workbook = Workbook()
    workbook = create_excel_cheet_for_stats(workbook, draw_imgs_reports, DrawImgsStat, draw_imgs_stat_fields)
    workbook = create_excel_cheet_for_stats(workbook, net_compile_reports, NetCompilationStat, net_compile_stat_fields)
    workbook = create_excel_cheet(workbook, net_compile_reports, net_compile_reports_draw_fields, vertical=True)
    workbook = create_excel_cheet(workbook, draw_imgs_reports, draw_imgs_reports_draw_fields, vertical=True)
    workbook = create_excel_cheet(workbook, metrics_report_common_statistic, metrics_report_common_statistic_draw_fields)
    workbook = create_excel_net_draw_cheet(workbook,
                                           net_compile_reports, net_compile_fields_common_report,
                                           draw_imgs_reports, draw_imgs_fields_common_report,
                                           draw_imgs_amount,
                                           vertical=True)
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
    net_compile_reports_draw_fields = ['create_date_time', 'status', 'date_time_finish', 'name', 'ip',
                                       'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100']
    draw_imgs_reports_draw_fields = ['create_date_time', 'status', 'date_time_finish', 'name', 'ip',
                                     'p50', 'p75', 'p90', 'p95', 'p96', 'p97', 'p98', 'p99', 'p100']

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-metric_report.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
    )

    workbook = Workbook()
    workbook = create_excel_cheet(workbook, net_compile_reports, net_compile_reports_draw_fields)
    workbook = create_excel_cheet(workbook, draw_imgs_reports, draw_imgs_reports_draw_fields)
    workbook.save(response)
    return response
