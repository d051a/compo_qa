from django.db.models import F
from main.models import DrawImgsReport, MetricReport, DrawImgsStat


def get_drawed_entry_by_percent(percent, time_report_start, query):
    drawed_esl = dict()
    try:
        report_statistics_query = query.order_by('date_time').filter(images_succeeded__gte=(F('total_esl') / 100 * percent))[0]
    except:
        drawed_esl['images_succeeded'] = ''
        drawed_esl['elapsed_time_after_start'] = ''
        drawed_esl['total_esl'] = ''
        drawed_esl['date_time'] = ''
        return drawed_esl
    hours, mins, secs = str(report_statistics_query.date_time - time_report_start).split(':')
    drawed_esl['images_succeeded'] = report_statistics_query.images_succeeded
    drawed_esl['elapsed_time_after_start'] = f'{hours}:{mins}:{secs[:2]}'
    drawed_esl['total_esl'] = report_statistics_query.total_esl
    drawed_esl['date_time'] = report_statistics_query.date_time
    return drawed_esl


def get_drawed_imgs_percent_table_tds(metric_report):
    drawed_percent_points = [50, 75, 90, 95, 96, 97, 98, 99, 100]
    draw_reports_imgs_stats = {}
    draw_reports = DrawImgsReport.objects.filter(metric_report=metric_report)
    for draw_report in draw_reports:
        draw_imgs_stats = DrawImgsStat.objects.filter(draw_imgs_report=draw_report).order_by('percent_step')
        percents_list = [(draw_stat.percent_step, draw_stat.elapsed_time) for draw_stat in draw_imgs_stats]
        draw_reports_imgs_stats[draw_report.pk] = percents_list

    header = ''
    for draw_imgs_report in draw_reports:
        header += f'<th>{draw_imgs_report.create_date_time}</th>'
    header = f'<tr><th>%</th>{header}</tr>'

    # print(header)
    # print(draw_reports_imgs_stats)

    strings = []

    for draw_report in draw_reports_imgs_stats:
        for elem in draw_reports_imgs_stats[draw_report]:
            for percent in drawed_percent_points:
                if percent == elem[0]:
                    strings.append(elem)
                else:
                    strings.append('')
    print(strings)






