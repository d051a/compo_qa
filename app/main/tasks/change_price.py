import traceback
import random


import_file_path = '280920061050.dat'
output_file_path = '280920061050_new.dat'


def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8')as f:
            lines = f.readlines()
            return lines
    except Exception as error:
        print(f'read_file error: {error}')
        traceback.print_exc()
        print('Не удалось прочитать файл')
        return False


def add_lines_to_file(file_path, lines):
    try:
        with open(file_path, 'a', newline='\n')as file:
            for line in lines:
                file.write(line)
    except Exception as error:
        print(f'add_lines_to_file error: {error}')
        traceback.print_exc()


def chage_price_in_string(line, price):
    parsed_line = line.split(';')
    if len(parsed_line) > 5:
        if parsed_line[6] != 'Цена':
            parsed_line[6] = price
    string_with_new_price = make_string(parsed_line, ';')
    return string_with_new_price


def make_string(input_object, separator):
    string_processed = ''
    for item in input_object:
        string_processed += str(item) + separator
    return string_processed[0:len(string_processed)-1:]


def dat_file_change_prices(input_file_path, path_output_file):
    print('INFO: Инициация обработки dat-файла')
    prices = ['1,01', '111,10', '222,22', '333,33', '444,44', '555,55', '667,00', '777,77', '888,80', '999,99']
    input_lines = read_file(input_file_path)
    output_lines = []
    random_price_num = random.randint(0, len(prices) - 1)
    try:
        for line in input_lines:
            new_price = prices[random_price_num]
            string_with_new_price = chage_price_in_string(line, new_price)
            output_lines.append(string_with_new_price)
        add_lines_to_file(path_output_file, output_lines)
        print('INFO: Успешное завершение обработки dat-файла')
        return True
    except Exception as error:
        print(f'Не удалось изменить цены в файле {input_file_path}. Ошибка: ')
        print(error)
        return False


if __name__ == '__main__':
    dat_file_change_prices(import_file_path, output_file_path)
