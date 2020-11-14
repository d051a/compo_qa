import django
import os
from main.models import DrawImgsStat, NetCompilationStat, Statistic, NetCompileReport, DrawImgsReport, Configuration
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Font, Alignment
from main.excel_reports.excel_generics import insert_data_to_cell, expands_columns_width, step_enumerate,\
    add_table_titles, add_table_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()


def get_columns_ids(model_included_columns, reports_list):
    columns = []
    columns_ids = []
    db_model_fields = [field.name for field in reports_list.model._meta.fields]

    for num, field in enumerate(model_included_columns):
        if field in db_model_fields:
            columns.append(reports_list.model._meta.get_field(field).verbose_name)
            columns_ids.append(db_model_fields.index(field))
    return columns, columns_ids


def generate_table_data(worksheet, reports_list, model_included_columns, vertical=False,
                        start_row_num=1, alignment='center'):
    columns_and_ids = get_columns_ids(model_included_columns, reports_list)
    columns = columns_and_ids[0]
    columns_ids = columns_and_ids[1]
    colon_or_row_num = 1
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                         bottom=Side(style='thin'))

    # создание шапки таблицы
    for elem_num, column_title in enumerate(columns, start_row_num):
        if vertical:
            cell = worksheet.cell(row=elem_num, column=colon_or_row_num)
        else:
            cell = worksheet.cell(row=colon_or_row_num, column=elem_num)
        cell.value = column_title
        cell.border = thin_border
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # заполнение таблицы даными
    for stat in reports_list.values_list():
        colon_or_row_num += 1
        row = [stat[stat_id] for stat_id in columns_ids]
        for elem_num, cell_value in enumerate(row, start_row_num):
            if vertical:
                cell = worksheet.cell(row=elem_num, column=colon_or_row_num)
            else:
                cell = worksheet.cell(row=colon_or_row_num, column=elem_num)
            cell.value = cell_value
            cell.border = thin_border
            cell.alignment = Alignment(horizontal=alignment)
    return worksheet


def create_excel_cheet(workbook, reports_list, model_included_columns, vertical=False, alignment='center'):
    worksheet = workbook.create_sheet(reports_list.model._meta.verbose_name_plural.title(), 0)
    worksheet_with_data = generate_table_data(worksheet, reports_list, model_included_columns,
                                              vertical=vertical, alignment=alignment)
    # увеличение ширины колонок
    expands_columns_width(worksheet_with_data)
    return workbook


def create_excel_cheet_for_stats(workbook, reports_list, report_stats_model, print_columns, vertical=False):
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                         bottom=Side(style='thin'))

    for report in reports_list:
        if report_stats_model == DrawImgsStat:
            statistic_objects = DrawImgsStat.objects.filter(draw_imgs_report=report)
        if report_stats_model == NetCompilationStat:
            statistic_objects = NetCompilationStat.objects.filter(net_compile_report=report)
        row_num = 1
        colon_num = 1
        worksheet = workbook.create_sheet(report.__str__(), 0)
        columns = []
        columns_ids = []
        db_model_fields = report_stats_model._meta.fields

        for num, field in enumerate(db_model_fields):
            if field.name in print_columns:
                columns.append(report_stats_model._meta.get_field(field.name).verbose_name)
                columns_ids.append(num)

        # создание шапки таблицы
        for elem_num, column_title in enumerate(columns, 1):
            if vertical:
                cell = worksheet.cell(row=elem_num, column=colon_num)
            else:
                cell = worksheet.cell(row=row_num, column=elem_num)
            cell.value = column_title
            cell.border = thin_border
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # заполнение таблицы даными
        for statistic_object in statistic_objects.values_list():
            row_num += 1
            colon_num += 1
            rows_list = [statistic_object[stat_id] for stat_id in columns_ids]
            for elem_num, cell_value in enumerate(rows_list, 1):
                if vertical:
                    cell = worksheet.cell(row=elem_num, column=colon_num)
                else:
                    cell = worksheet.cell(row=row_num, column=elem_num)
                cell.value = cell_value
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center')

        # увеличение ширины колонок
        expands_columns_width(worksheet)
    return workbook


def create_draw_imgs_stats_sheet(workbook, report, vertical=False, start_position=1):
    report_statistics = DrawImgsStat.objects.filter(draw_imgs_report=report)
    worksheet = workbook.create_sheet(report.__str__(), 0)
    titles = {1: 'Процент отрисовки',
              2: 'Затраченное время',
              3: 'Отрисованных ценников'}
    # создание шапки таблицы
    add_table_titles(worksheet, titles, vertical=vertical, bolt=True)

    start_position += 1
    for elem_num, statistic in enumerate(report_statistics, start_position):
        if vertical:
            insert_data_to_cell(worksheet, statistic.percent_step, 1, elem_num)
            insert_data_to_cell(worksheet, statistic.elapsed_time, 2, elem_num)
            insert_data_to_cell(worksheet, statistic.images_succeeded, 3, elem_num)
        else:
            insert_data_to_cell(worksheet, statistic.percent_step, elem_num, 1)
            insert_data_to_cell(worksheet, statistic.elapsed_time, elem_num, 2)
            insert_data_to_cell(worksheet, statistic.images_succeeded, elem_num, 3)
    # увеличение ширины колонок
    expands_columns_width(worksheet)
    return workbook


def create_net_compile_stats_sheet(workbook, report, vertical=False, start_position=1):
    report_statistics = NetCompilationStat.objects.filter(net_compile_report=report)
    worksheet = workbook.create_sheet(report.__str__(), 0)

    titles = {1: 'Ценников онлайн',
              2: 'Компиляция сети (%)',
              3: 'Затраченное время'}

    # создание шапки таблицы
    add_table_titles(worksheet, titles, vertical=vertical, bolt=True)
        
    # заполнение таблицы даными
    start_position += 1
    for elem_num, statistic in enumerate(report_statistics, start_position):
        if vertical:
            insert_data_to_cell(worksheet, statistic.online_esl, 1, elem_num)
            insert_data_to_cell(worksheet, statistic.compilation_percent, 2, elem_num)
            insert_data_to_cell(worksheet, statistic.elapsed_time, 3, elem_num)
        else:
            insert_data_to_cell(worksheet, statistic.online_esl, elem_num, 1)
            insert_data_to_cell(worksheet, statistic.compilation_percent, elem_num, 2)
            insert_data_to_cell(worksheet, statistic.elapsed_time, elem_num, 3)
    # увеличение ширины колонок
    expands_columns_width(worksheet)
    return workbook


def create_all_statistics_sheet(workbook, report, report_start_time, report_finish_time, vertical=False, start_position=1):
    report_statistics = Statistic.objects.filter(metric_report=report).filter(
        date_time__range=(report_start_time, report_finish_time)).order_by('date_time')
    worksheet = workbook.create_sheet('Общая статистика', 0)

    titles = {1: 'Дата и время',
              2: 'total_nodes',
              3: 'inaccessible_nodes',
              4: 'total_number_routes',
              5: 'maximum_road_length',
              6: 'average_route_length',
              7: 'accessible_nodes_percent',
              8: 'elapsed_time',
              9: 'total_esl',
              10: 'online_esl',
              11: 'images_in_transit',
              12: 'images_in_draw',
              13: 'images_in_resend_queue',
              14: 'images_succeeded',
              15: 'images_failed',
              16: 'currently_scanning',
              17: 'network_mode',
              18: 'connects',
              19: 'network_mode_percent',
              20: 'voltage_average',
              21: 'voltage_current',
              22: 'voltage_max',
              23: 'bat_reserved1',
              24: 'bat_reserved2',
              25: 'bat_reserved3',
              26: 'bat_reserved4',
              }
    # создание шапки таблицы
    add_table_titles(worksheet, titles, vertical=vertical, bolt=True)

    # заполнение таблицы даными
    start_position += 1
    for elem_num, statistic in enumerate(report_statistics, start_position):
        if vertical:
            insert_data_to_cell(worksheet, statistic.date_time, 1, elem_num)
            insert_data_to_cell(worksheet, statistic.total_nodes, 2, elem_num)
            insert_data_to_cell(worksheet, statistic.inaccessible_nodes, 3,  elem_num)
            insert_data_to_cell(worksheet, statistic.total_number_routes, 4, elem_num)
            insert_data_to_cell(worksheet, statistic.maximum_road_length, 5, elem_num)
            insert_data_to_cell(worksheet, statistic.average_route_length, 6, elem_num)
            insert_data_to_cell(worksheet, statistic.accessible_nodes_percent, 7, elem_num)
            insert_data_to_cell(worksheet, statistic.elapsed_time, 8, elem_num)
            insert_data_to_cell(worksheet, statistic.total_esl, 9, elem_num)
            insert_data_to_cell(worksheet, statistic.online_esl, 10, elem_num)
            insert_data_to_cell(worksheet, statistic.images_in_transit, 11, elem_num)
            insert_data_to_cell(worksheet, statistic.images_in_draw, 12, elem_num)
            insert_data_to_cell(worksheet, statistic.images_in_resend_queue, 13, elem_num)
            insert_data_to_cell(worksheet, statistic.images_succeeded, 14, elem_num)
            insert_data_to_cell(worksheet, statistic.images_failed, 15, elem_num)
            insert_data_to_cell(worksheet, statistic.currently_scanning, 16, elem_num)
            insert_data_to_cell(worksheet, statistic.network_mode, 17, elem_num)
            insert_data_to_cell(worksheet, statistic.connects, 18, elem_num)
            insert_data_to_cell(worksheet, statistic.network_mode_percent, 19, elem_num)
            insert_data_to_cell(worksheet, statistic.voltage_average, 20, elem_num)
            insert_data_to_cell(worksheet, statistic.voltage_current, 21, elem_num)
            insert_data_to_cell(worksheet, statistic.voltage_max, 22, elem_num)
            insert_data_to_cell(worksheet, statistic.bat_reserved1, 23, elem_num)
            insert_data_to_cell(worksheet, statistic.bat_reserved2, 24, elem_num)
            insert_data_to_cell(worksheet, statistic.bat_reserved3, 25, elem_num)
            insert_data_to_cell(worksheet, statistic.bat_reserved4, 26, elem_num)
        else:
            insert_data_to_cell(worksheet, statistic.date_time, elem_num, 1)
            insert_data_to_cell(worksheet, statistic.total_nodes, elem_num, 2)
            insert_data_to_cell(worksheet, statistic.inaccessible_nodes, elem_num, 3)
            insert_data_to_cell(worksheet, statistic.total_number_routes, elem_num, 4)
            insert_data_to_cell(worksheet, statistic.maximum_road_length, elem_num, 5)
            insert_data_to_cell(worksheet, statistic.average_route_length, elem_num, 6)
            insert_data_to_cell(worksheet, statistic.accessible_nodes_percent, elem_num, 7)
            insert_data_to_cell(worksheet, statistic.elapsed_time, elem_num, 8)
            insert_data_to_cell(worksheet, statistic.total_esl, elem_num, 9)
            insert_data_to_cell(worksheet, statistic.online_esl, elem_num, 10)
            insert_data_to_cell(worksheet, statistic.images_in_transit, elem_num, 11)
            insert_data_to_cell(worksheet, statistic.images_in_draw, elem_num, 12)
            insert_data_to_cell(worksheet, statistic.images_in_resend_queue, elem_num, 13)
            insert_data_to_cell(worksheet, statistic.images_succeeded, elem_num, 14)
            insert_data_to_cell(worksheet, statistic.images_failed, elem_num, 15)
            insert_data_to_cell(worksheet, statistic.currently_scanning, elem_num, 16)
            insert_data_to_cell(worksheet, statistic.network_mode, elem_num, 17)
            insert_data_to_cell(worksheet, statistic.connects, elem_num, 18)
            insert_data_to_cell(worksheet, statistic.network_mode_percent, elem_num, 19)
            insert_data_to_cell(worksheet, statistic.voltage_average, elem_num, 20)
            insert_data_to_cell(worksheet, statistic.voltage_current, elem_num, 21)
            insert_data_to_cell(worksheet, statistic.voltage_max, elem_num, 22)
            insert_data_to_cell(worksheet, statistic.bat_reserved1, elem_num, 23)
            insert_data_to_cell(worksheet, statistic.bat_reserved2, elem_num, 24)
            insert_data_to_cell(worksheet, statistic.bat_reserved3, elem_num, 25)
            insert_data_to_cell(worksheet, statistic.bat_reserved4, elem_num, 26)

    # увеличение ширины колонок
    expands_columns_width(worksheet)
    return workbook


def create_common_sheet(workbook, metric_report, vertical=False, start_position=1):
    net_reports = NetCompileReport.objects.filter(metric_report=metric_report)
    draw_reports = DrawImgsReport.objects.filter(metric_report=metric_report)
    worksheet = workbook.create_sheet('Сводный отчет', 0)

    titles = {1:'Дата и время начала сборки',
              2: 'Время сборки сети',
              3: 'Процент сборки сети',
              4: 'Собранность сети за 60 мин.,%',
              5: 'Фактическое количество ESL',
              6: 'Статус',
              7: 'Среднее значение потребления в процессе сборки, mA',
              8: 'Время отрисовки 50%',
              9: 'Время отрисовки 75%',
              10: 'Время отрисовки 90%',
              11: 'Время отрисовки 95%',
              12: 'Время отрисовки 96%',
              13: 'Время отрисовки 97%',
              14: 'Время отрисовки 98%',
              15: 'Время отрисовки 99%',
              16: 'Время отрисовки 99.5%',
              17: 'Время отрисовки 99.9%',
              18: 'Время отрисовки 100%',
              19: 'Не отрисовано, шт ',
              20: 'Среднее значение потребления в процессе отрисовки, mA',
              21: 'Среднее значение потребления (общее), mA'
              }

    # создание шапки таблицы
    add_table_titles(worksheet, titles, vertical=vertical, bolt=True)

    # Расширение колонок
    expands_columns_width(worksheet)

    # заполнение таблицы даными
    start_position += 1
    merge_cell_num = metric_report.draw_imgs_amount
    for elem_num, report in step_enumerate(net_reports, start_position, merge_cell_num):
        if vertical:
            insert_data_to_cell(worksheet, report.create_date_time, 1, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.elapsed_time, 2, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.final_percent, 3, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t60, 4, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.fact_total_esl, 5, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.status, 6, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.voltage_average, 7, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
        else:
            insert_data_to_cell(worksheet, report.create_date_time, elem_num, 1, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.elapsed_time, elem_num, 2, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.final_percent, elem_num, 3, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t60, elem_num, 4, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.fact_total_esl, elem_num, 5, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.status, elem_num, 6, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.voltage_average, elem_num, 7, merge=True, merge_num=merge_cell_num, vertical=vertical)

    for elem_num, report in enumerate(draw_reports, start_position):
        if vertical:
            insert_data_to_cell(worksheet, report.p50, 8, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p75, 9, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p90, 10, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p95, 11, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p96, 12, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p97, 13, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p98, 14, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p99, 15, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p995, 16, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p999, 17, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p100, 18, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.not_drawed_esl, 19, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.voltage_average, 20, elem_num, vertical=vertical)
        else:
            insert_data_to_cell(worksheet, report.p50, elem_num, 8, vertical=vertical)
            insert_data_to_cell(worksheet, report.p75, elem_num, 9, vertical=vertical)
            insert_data_to_cell(worksheet, report.p90, elem_num, 10, vertical=vertical)
            insert_data_to_cell(worksheet, report.p95, elem_num, 11, vertical=vertical)
            insert_data_to_cell(worksheet, report.p96, elem_num, 12, vertical=vertical)
            insert_data_to_cell(worksheet, report.p97, elem_num, 13, vertical=vertical)
            insert_data_to_cell(worksheet, report.p98, elem_num, 14, vertical=vertical)
            insert_data_to_cell(worksheet, report.p99, elem_num, 15, vertical=vertical)
            insert_data_to_cell(worksheet, report.p995, elem_num, 16, vertical=vertical)
            insert_data_to_cell(worksheet, report.p999, elem_num, 17, vertical=vertical)
            insert_data_to_cell(worksheet, report.p100, elem_num, 18, vertical=vertical)
            insert_data_to_cell(worksheet, report.not_drawed_esl, elem_num, 19, vertical=vertical)
            insert_data_to_cell(worksheet, report.voltage_average, elem_num, 20, vertical=vertical)

        merge_voltage_cell_num = metric_report.net_compile_amount * metric_report.draw_imgs_amount
        common_voltage_average = metric_report.voltage_average
        if vertical:
            insert_data_to_cell(worksheet, common_voltage_average, 21, start_position, merge=True,
                                merge_num=merge_voltage_cell_num, vertical=vertical)
        else:
            insert_data_to_cell(worksheet, common_voltage_average, 21, start_position, merge=True,
                                merge_num=merge_voltage_cell_num, vertical=vertical)
    return workbook


def create_common_expanded_sheet(workbook, metric_report, vertical=False, start_position=1):
    net_reports = NetCompileReport.objects.filter(metric_report=metric_report)
    draw_reports = DrawImgsReport.objects.filter(metric_report=metric_report)
    worksheet = workbook.create_sheet('Сводный отчет (расширенный)', 0)

    titles = {1: 'Дата и время начала сборки',
              2: 'Время сборки сети',
              3: 'Процент сборки сети',
              4: 'Статус',
              5: 'Время сборки 10%',
              6: 'Время сборки 20%',
              7: 'Время сборки 30%',
              8: 'Время сборки 40%',
              9: 'Время сборки 50%',
              10: 'Время сборки 75%',
              11: 'Время сборки 90%',
              12: 'Время сборки 95%',
              13: 'Время сборки 96%',
              14: 'Время сборки 97%',
              15: 'Время сборки 98%',
              16: 'Время сборки 99%',
              17: 'Время сборки 99.5%',
              18: 'Время сборки 99.9%',
              19: 'Время сборки 100%',
              20: 'Собранность сети за 10 мин., %',
              21: 'Собранность сети за 20 мин., %',
              22: 'Собранность сети за 30 мин., %',
              23: 'Собранность сети за 40 мин., %',
              24: 'Собранность сети за 50 мин., %',
              25: 'Собранность сети за 60 мин., %',
              26: 'Собранность сети за 70 мин., %',
              27: 'Собранность сети за 80 мин., %',
              28: 'Собранность сети за 90 мин., %',
              29: 'Собранность сети за 100 мин., %',
              30: 'Собранность сети за 110 мин., %',
              31: 'Собранность сети за 120 мин., %',
              32: 'Собранность сети за 130 мин., %',
              33: 'Собранность сети за 140 мин., %',
              34: 'Собранность сети за 150 мин., %',
              35: 'Фактическое количество ESL',
              36: 'Сборка считается успешной при, %',
              37: 'Среднее значение потребления в процессе сборки, mA',
              38: 'Дата и время создания отчета',
              39: 'Дата и время окончания отчета',
              40: 'Предельное время отрисовки, мин',
              41: 'Время отрисовки 10%',
              42: 'Время отрисовки 20%',
              43: 'Время отрисовки 30%',
              44: 'Время отрисовки 40%',
              45: 'Время отрисовки 50%',
              46: 'Время отрисовки 75%',
              47: 'Время отрисовки 90%',
              48: 'Время отрисовки 95%',
              49: 'Время отрисовки 96%',
              50: 'Время отрисовки 97%',
              51: 'Время отрисовки 98%',
              52: 'Время отрисовки 99%',
              53: 'Время отрисовки 99.5%',
              54: 'Время отрисовки 99.9%',
              55: 'Время отрисовки 100%',
              56: 'Отрисовано за 10 мин., %',
              57: 'Отрисовано за 20 мин., %',
              58: 'Отрисовано за 30 мин., %',
              59: 'Отрисовано за 40 мин., %',
              60: 'Отрисовано за 50 мин., %',
              61: 'Отрисовано за 60 мин., %',
              62: 'Отрисовано за 70 мин., %',
              63: 'Отрисовано за 80 мин., %',
              64: 'Отрисовано за 90 мин., %',
              65: 'Отрисовано за 100 мин., %',
              66: 'Отрисовано за 110 мин., %',
              67: 'Отрисовано за 120 мин., %',
              68: 'Отрисовано за 130 мин., %',
              69: 'Отрисовано за 140 мин., %',
              70: 'Отрисовано за 150 мин., %',
              71: 'Не отрисовано, шт ',
              72: 'Отрисовано ценников, шт',
              73: 'Процент отрисовки',
              74: 'Тип отрисовки ценников',
              75: 'Статус',
              76: 'Среднее значение потребления в процессе отрисовки, mA',
              }

    # создание шапки таблицы
    add_table_titles(worksheet, titles, vertical=vertical, bolt=True)

    # Расширение колонок
    expands_columns_width(worksheet)

    # заполнение таблицы даными
    start_position += 1

    merge_cell_num = metric_report.draw_imgs_amount
    merge_voltage_cell_num = metric_report.net_compile_amount * metric_report.draw_imgs_amount
    common_voltage_average = metric_report.voltage_average
    for elem_num, report in step_enumerate(net_reports, start_position, merge_cell_num):
        if vertical:
            insert_data_to_cell(worksheet, report.create_date_time, 1, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.elapsed_time, 2, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.final_percent, 3, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.status, 4, elem_num, merge=True, merge_num=merge_cell_num,vertical=vertical)
            insert_data_to_cell(worksheet, report.p10, 5, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p20, 6, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p30, 7, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p40, 8, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p50, 9, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p75, 10, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p90, 11, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p95, 12, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p96, 13, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p97, 14, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p98, 15, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p99, 16, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p995, 17, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p999, 18, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p100, 19, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t10, 20, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t20, 21, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t30, 22, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t40, 23, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t50, 24, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t60, 25, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t70, 26, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t80, 27, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t90, 28, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t100, 29, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t110, 30, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t120, 31, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t130, 32, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t140, 33, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t150, 34, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.fact_total_esl, 35, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.success_percent, 36, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.voltage_average, 37, elem_num, merge=True, merge_num=merge_cell_num, vertical=vertical)

        else:
            insert_data_to_cell(worksheet, report.create_date_time, elem_num, 1, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.elapsed_time, elem_num, 2, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.final_percent, elem_num, 3, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.status, elem_num, 4, merge=True, merge_num=merge_cell_num,vertical=vertical)
            insert_data_to_cell(worksheet, report.p10, elem_num, 5, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p20, elem_num, 6, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p30, elem_num, 7, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p40, elem_num, 8, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p50, elem_num, 9, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p75, elem_num, 10, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p90, elem_num, 11, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p95, elem_num, 12, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p96, elem_num, 13, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p97, elem_num, 14, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p98, elem_num, 15, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p99, elem_num, 16, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p995, elem_num, 17, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p999, elem_num, 18, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p100, elem_num, 19, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t10, elem_num, 20, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t20, elem_num, 21, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t30, elem_num, 22, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t40, elem_num, 23, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t50, elem_num, 24, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t60, elem_num, 25, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t70, elem_num, 26, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t80, elem_num, 27, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t90, elem_num, 28, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t100, elem_num, 29, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t110, elem_num, 30, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t120, elem_num, 31, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t130, elem_num, 32, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t140, elem_num, 33, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t150, elem_num, 34, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.fact_total_esl, elem_num, 35, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.success_percent, elem_num, 36, merge=True, merge_num=merge_cell_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.voltage_average, elem_num, 37, merge=True, merge_num=merge_cell_num, vertical=vertical)

    for elem_num, report in enumerate(draw_reports, start_position):
        if vertical:
            insert_data_to_cell(worksheet, report.create_date_time, 38, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.date_time_finish, 39, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.draw_imgs_limit_mins, 40, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p10, 41, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p20, 42, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p30, 43, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p40, 44, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p50, 45, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p75, 46, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p90, 47, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p95, 48, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p96, 49, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p97, 50, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p98, 51, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p99, 52, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p995, 53, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p999, 54, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.p100, 55, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t10, 56, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t20, 57, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t30, 58, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t40, 59, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t50, 60, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t60, 61, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t70, 62, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t80, 63, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t90, 64, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t100, 65, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t110, 66, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t120, 67, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t130, 68, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t140, 69, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.t150, 70, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.not_drawed_esl, 71, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.drawed_esl, 72, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.final_percent, 73, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.draw_imgs_type, 74, elem_num, vertical=vertical)
            insert_data_to_cell(worksheet, report.status, 75, elem_num, vertical=vertical)
        else:
            insert_data_to_cell(worksheet, report.create_date_time, elem_num, 38, vertical=vertical)
            insert_data_to_cell(worksheet, report.date_time_finish, elem_num, 39, vertical=vertical)
            insert_data_to_cell(worksheet, report.draw_imgs_limit_mins, elem_num, 40, vertical=vertical)
            insert_data_to_cell(worksheet, report.p10, elem_num, 41, vertical=vertical)
            insert_data_to_cell(worksheet, report.p20, elem_num, 42, vertical=vertical)
            insert_data_to_cell(worksheet, report.p30, elem_num, 43, vertical=vertical)
            insert_data_to_cell(worksheet, report.p40, elem_num, 44, vertical=vertical)
            insert_data_to_cell(worksheet, report.p50, elem_num, 45, vertical=vertical)
            insert_data_to_cell(worksheet, report.p75, elem_num, 46, vertical=vertical)
            insert_data_to_cell(worksheet, report.p90, elem_num, 47, vertical=vertical)
            insert_data_to_cell(worksheet, report.p95, elem_num, 48, vertical=vertical)
            insert_data_to_cell(worksheet, report.p96, elem_num, 49, vertical=vertical)
            insert_data_to_cell(worksheet, report.p97, elem_num, 50, vertical=vertical)
            insert_data_to_cell(worksheet, report.p98, elem_num, 51, vertical=vertical)
            insert_data_to_cell(worksheet, report.p99, elem_num, 52, vertical=vertical)
            insert_data_to_cell(worksheet, report.p995, elem_num, 53, vertical=vertical)
            insert_data_to_cell(worksheet, report.p999, elem_num, 54, vertical=vertical)
            insert_data_to_cell(worksheet, report.p100, elem_num, 55, vertical=vertical)
            insert_data_to_cell(worksheet, report.t10, elem_num, 56, vertical=vertical)
            insert_data_to_cell(worksheet, report.t20, elem_num, 57, vertical=vertical)
            insert_data_to_cell(worksheet, report.t30, elem_num, 58, vertical=vertical)
            insert_data_to_cell(worksheet, report.t40, elem_num, 59, vertical=vertical)
            insert_data_to_cell(worksheet, report.t50, elem_num, 60, vertical=vertical)
            insert_data_to_cell(worksheet, report.t60, elem_num, 61, vertical=vertical)
            insert_data_to_cell(worksheet, report.t70, elem_num, 62, vertical=vertical)
            insert_data_to_cell(worksheet, report.t80, elem_num, 63, vertical=vertical)
            insert_data_to_cell(worksheet, report.t90, elem_num, 64, vertical=vertical)
            insert_data_to_cell(worksheet, report.t100, elem_num, 65, vertical=vertical)
            insert_data_to_cell(worksheet, report.t110, elem_num, 66, vertical=vertical)
            insert_data_to_cell(worksheet, report.t120, elem_num, 67, vertical=vertical)
            insert_data_to_cell(worksheet, report.t130, elem_num, 68, vertical=vertical)
            insert_data_to_cell(worksheet, report.t140, elem_num, 69, vertical=vertical)
            insert_data_to_cell(worksheet, report.t150, elem_num, 70, vertical=vertical)
            insert_data_to_cell(worksheet, report.not_drawed_esl, elem_num, 71, vertical=vertical)
            insert_data_to_cell(worksheet, report.drawed_esl, elem_num, 72, vertical=vertical)
            insert_data_to_cell(worksheet, report.final_percent, elem_num, 73, vertical=vertical)
            insert_data_to_cell(worksheet, report.draw_imgs_type, elem_num, 74, vertical=vertical)
            insert_data_to_cell(worksheet, report.status, elem_num, 75, vertical=vertical)

        if vertical:
            insert_data_to_cell(worksheet, common_voltage_average, 76, start_position, merge=True,
                                merge_num=merge_voltage_cell_num, vertical=vertical)
        else:
            insert_data_to_cell(worksheet, common_voltage_average, 76, start_position, merge=True,
                                merge_num=merge_voltage_cell_num, vertical=vertical)
    return workbook


def create_configuration_sheet(workbook, metric_report, vertical=False, start_position=1):
    worksheet = workbook.create_sheet('Конфигурация', 0)
    report = Configuration.objects.get(metric_report=metric_report)

    titles = {1: 'Номера щитов',
              2: 'Конфигурация системы',
              3: 'Количество ценников стенда, шт',
              4: 'Количество РУ, шт',
              5: 'Конфигурация РУ',
              6: 'Количество донглов на РУ, шт',
              7: 'Версия СУМ',
              8: 'Версия Хаоса',
              9: 'Число этажей дерева',
              10: 'Версия драйвера',
              11: 'Версия прошивки ЭЦ',
              12: 'HW версия ЭЦ',
              13: 'HW версия донглов'
              }

    # создание шапки таблицы
    add_table_titles(worksheet, titles, vertical=vertical, bolt=True)

    # заполнение таблицы даными
    start_position += 1
    fields = {1: report.shields_num,
              2: report.hardware_config,
              3: report.total_esl,
              4: report.dd_nums,
              5: report.dd_configuration,
              6: report.dd_dongles_num,
              7: report.version_sum,
              8: report.version_chaos,
              9: report.tree_floor_num,
              10: report.version_driver,
              11: report.version_esl_firmware,
              12: report.version_esl_hw,
              13: report.version_dongles_hw,
              }

    # добавление данных в ячейки
    add_table_data(worksheet, fields, vertical=vertical, start_position=start_position)

    # Расширение колонок
    expands_columns_width(worksheet)
    return workbook

if __name__ == '__main__':
    pass
