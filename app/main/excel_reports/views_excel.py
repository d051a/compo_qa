from main.models import Statistic,  MetricReport, Chaos, DrawImgsReport,\
    NetCompileReport, DrawImgsStat, NetCompilationStat, Configuration
from main.excel_reports.excel_tools import create_excel_cheet, create_excel_cheet_for_stats, create_excel_net_draw_cheet
from django.http import HttpResponse
from datetime import datetime
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
    net_compile_reports = NetCompileReport.objects.filter(metric_report=metrics_report)
    draw_imgs_reports = DrawImgsReport.objects.filter(metric_report=metrics_report)
    metrics_report_common_statistic = Statistic.objects.filter(metric_report=metrics_report).order_by('date_time')
    configuration = Configuration.objects.filter(metric_report=metrics_report)
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
    response['Content-Disposition'] = 'attachment; filename={date}-metric_report.xlsx'.format(
        date=datetime.now().strftime('%d.%m.%Y_%H.%M.%S'),
    )

    workbook = Workbook()
    workbook = create_excel_cheet(workbook, net_compile_reports, net_compile_short_report_draw_fields)
    workbook = create_excel_cheet(workbook, draw_imgs_reports, draw_imgs_stats_short_report_draw_fields)
    workbook.save(response)
    return response
