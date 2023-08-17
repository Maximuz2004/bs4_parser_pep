import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, FILE_MODE,
                       PRETTY_MODE, RESULT_DIR)

FILE_SAVED_MESSAGE = 'Файл с результатами был сохранен: {}'
TABLE_ALING = 'l'


def control_output(results, cli_args):
    output_functions = {
        FILE_MODE: file_output,
        PRETTY_MODE: pretty_output,
    }
    output_functions.get(cli_args.output, default_output)(results, cli_args)


def default_output(*args):
    for row in args[0]:
        print(*row)


def pretty_output(*args):
    results = args[0]
    table = PrettyTable()
    table.field_names = results[0]
    table.aling = TABLE_ALING
    table.add_rows(results[1:])
    print(table)


def file_output(*args):
    results_dir = BASE_DIR / RESULT_DIR
    results_dir.mkdir(exist_ok=True)
    file_path = (results_dir /
                 f'{args[1].mode}_'
                 f'{dt.datetime.now().strftime(DATETIME_FORMAT)}.csv')
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(args[0])
    logging.info(FILE_SAVED_MESSAGE.format(file_path))
