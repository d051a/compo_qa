import django
import os
from main.models import DrawImgsStat, NetCompilationStat
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Font, Alignment


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()


def as_text(value):
    if value is None:
        return ""
    return str(value)


def expands_columns_width(worksheet):
    for column_cells in worksheet.columns:
        length = max(len(as_text(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = length
    return worksheet


def get_columns_ids(model_included_columns, reports_list):
    columns = []
    columns_ids = []
    db_model_fields = [field.name for field in reports_list.model._meta.fields]

    for num, field in enumerate(model_included_columns):
        if field in db_model_fields:
            columns.append(reports_list.model._meta.get_field(field).verbose_name)
            columns_ids.append(db_model_fields.index(field))
    return columns, columns_ids


def generate_table_data(worksheet, reports_list, model_included_columns, vertical=False, start_row_num=1):
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
            cell.alignment = Alignment(horizontal='left')
    return worksheet


def create_excel_cheet(workbook, reports_list, model_included_columns, vertical=False):
    worksheet = workbook.create_sheet(reports_list.model._meta.verbose_name_plural.title(), 0)
    worksheet_with_data = generate_table_data(worksheet, reports_list, model_included_columns, vertical=vertical)
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
                cell.alignment = Alignment(horizontal='left')

        # увеличение ширины колонок
        expands_columns_width(worksheet)
    return workbook


def create_excel_net_draw_cheet(workbook,
                                net_compile_reports,
                                net_compile_included_columns,
                                draw_imgs_reports,
                                draw_imgs_included_columns,
                                draw_imgs_amount,
                                report_name,
                                vertical=False):
    net_compile_reports = net_compile_reports.order_by('create_date_time')
    draw_imgs_reports = draw_imgs_reports.order_by('create_date_time')
    worksheet = workbook.create_sheet(report_name, 0)
    colon_or_row_num = 1
    columns = []
    columns_ids = []
    db_model_fields = [field.name for field in net_compile_reports.model._meta.fields]
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                         bottom=Side(style='thin'))

    for num, field in enumerate(net_compile_included_columns):
        if field in db_model_fields:
            columns.append(net_compile_reports.model._meta.get_field(field).verbose_name)
            columns_ids.append(db_model_fields.index(field))

    # создание шапки таблицы
    for elem_num, column_title in enumerate(columns, 1):
        if vertical:
            cell = worksheet.cell(row=elem_num, column=colon_or_row_num)
        else:
            cell = worksheet.cell(row=colon_or_row_num, column=elem_num)
        cell.value = column_title
        cell.border = thin_border
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    colon_or_row_num += 1
    # заполнение таблицы даными о сборках сети
    for stat in net_compile_reports.values_list():
        row = [stat[stat_id] for stat_id in columns_ids]
        for elem_num, cell_value in enumerate(row, 1):
            if vertical:
                worksheet.merge_cells(start_row=elem_num, start_column=colon_or_row_num, end_row=elem_num,
                                      end_column=colon_or_row_num+draw_imgs_amount-1)
                cell = worksheet.cell(row=elem_num, column=colon_or_row_num)
                cell.value = cell_value
                cell.alignment = Alignment(horizontal='left')
                for i in range(1, draw_imgs_amount):
                    cell.border = thin_border
                    cell = worksheet.cell(row=elem_num, column=colon_or_row_num+i)
                    cell.alignment = Alignment(horizontal='left')
            else:
                cell = worksheet.cell(row=colon_or_row_num, column=elem_num)
                cell.value = cell_value
                cell.border = thin_border
                cell = worksheet.cell(row=colon_or_row_num+1, column=elem_num)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='left')

            cell.border = thin_border
        colon_or_row_num += draw_imgs_amount

    start_row_num = len(net_compile_included_columns) + 1
    generate_table_data(worksheet, draw_imgs_reports, draw_imgs_included_columns,
                        vertical=True, start_row_num=start_row_num)
    # expands_columns_width(worksheet)
    return workbook


if __name__ == '__main__':
    pass
