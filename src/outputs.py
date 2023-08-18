import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, FILE_MODE,
                       PRETTY_MODE, RESULT_DIR)

FILE_SAVED_MESSAGE = 'Файл с результатами был сохранен: {}'
TABLE_ALING = 'l'


def default_output(results, cli_args):
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.aling = TABLE_ALING
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULT_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_path = results_dir / f'{parser_mode}_{now_formatted}.csv'
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, dialect=csv.unix_dialect).writerows(results)
    logging.info(FILE_SAVED_MESSAGE.format(file_path))


OUTPUT_FUNCTIONS = {
    FILE_MODE: file_output,
    PRETTY_MODE: pretty_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUT_FUNCTIONS.get(cli_args.output)(results, cli_args)
