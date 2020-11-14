from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Font, Alignment


def as_text(value):
    if value is None:
        return ""
    return str(value)


def expands_columns_width(worksheet):
    for column_cells in worksheet.columns:
        length = max(len(as_text(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = length
    return worksheet


def set_appearance(table_cell, border=True, bolt=True, horizontal_alignment='center'):
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                         bottom=Side(style='thin'))
    if border:
        table_cell.border = thin_border
    table_cell.font = Font(bold=bolt)
    table_cell.alignment = Alignment(horizontal=horizontal_alignment)


def insert_data_to_cell(worksheet, cell_value, row_num=1, coll_num=1, bolt=False,
                        merge=False, merge_num=1, vertical=True):
    if merge:
        if vertical:
            end_merge_num = coll_num + merge_num - 1
            print(f'start_row={row_num}, start_column={coll_num}, end_row={row_num},    end_column={end_merge_num}')
            worksheet.merge_cells(start_row=row_num, start_column=coll_num, end_row=row_num,
                                  end_column=end_merge_num)
            for i in range(1, merge_num + 1):
                cell = worksheet.cell(row=row_num, column=end_merge_num)
                set_appearance(cell, bolt=bolt)
        else:
            end_merge_num = row_num + merge_num
            print(f'start_row={row_num}, start_column={coll_num}, end_row={end_merge_num},    end_column={coll_num}')
            worksheet.merge_cells(start_row=row_num, start_column=coll_num, end_row=end_merge_num,
                                  end_column=coll_num)
            for i in range(1, merge_num + 1):
                cell = worksheet.cell(row=end_merge_num, column=coll_num)
                set_appearance(cell, bolt=bolt)
    cell = worksheet.cell(row=row_num, column=coll_num)
    cell.value = cell_value
    set_appearance(cell, bolt=bolt)


def step_enumerate(input_list, start=0, step=1):
    for elem in input_list:
        yield (start, elem)
        start += step


def add_table_titles(worksheet, titles, start_position=1, vertical=True, bolt=True):
    for position in titles.keys():
        if vertical:
            insert_data_to_cell(worksheet, titles[position], position, start_position, bolt=bolt)
        else:
            insert_data_to_cell(worksheet, titles[position], start_position, position, bolt=bolt)


def add_table_data(worksheet, fields, vertical=True, start_position=1):
    for position in fields.keys():
        print(position)
        if vertical:
            insert_data_to_cell(worksheet, fields[position], position, start_position)
        else:
            insert_data_to_cell(worksheet, fields[position], start_position, position)


def get_metric_report_id(id):
    url = f'http://172.16.25.10/metrics/{id}'
    return url