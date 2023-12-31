import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, FILE_MODE, LOG_DIR, LOG_FILE, PRETTY_MODE

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
PARSER_INFO = 'Парсер документации Python'
PARSER_HELP_MESSAGE = 'Режимы работы парсера'
CACHE_CLEAN_HELP_MESSAGE = 'Очистка кеша'
OUTPUT_HELP_MESSAGE = 'Дополнительные способы вывода данных'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description=PARSER_INFO)
    parser.add_argument(
        'mode',
        choices=available_modes,
        help=PARSER_HELP_MESSAGE
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help=CACHE_CLEAN_HELP_MESSAGE
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY_MODE, FILE_MODE),
        help=OUTPUT_HELP_MESSAGE
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / LOG_DIR
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / LOG_FILE
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
