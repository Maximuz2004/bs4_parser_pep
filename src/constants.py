from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
PEP_URL = 'https://peps.python.org/'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
MISMATCHED_STATUS = ("Несовпадающий статус:\n"
                     "{}\n"
                     "Статус в карточке: {}\n"
                     "Ожидаемые статусы: {}")
NOTHING_FIND_MESSAGE = 'Ничего не нашлось'
ARCHIVE_UPLOADED_MESSAGE = 'Архив был загружен и сохранен: {}'
PARSER_LAUNCHED_MESSAGE = 'Парсер запущен!'
COMMAND_LINE_ARGUMENTS = 'Аргументы коммандной строки: {}'
FINISH_WORK_MESSAGE = 'Парсер завершил работу'
FILE_SAVED_MESSAGE = 'Файл с результатами был сохранен: {}'
