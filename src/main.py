from collections import defaultdict
import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOAD_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       PEP_URL)

from exceptions import NothingFindException
from outputs import control_output
from utils import find_tag, get_soup

ARCHIVE_UPLOADED_MESSAGE = 'Архив был загружен и сохранен: {}'
BAD_URL_MESSAGE = 'Не удалось получить ответ для URL: {}'
ERROR_MESSAGE = 'Возникла ошибка при выполеннии парсинга: {}'
FINISH_WORK_MESSAGE = 'Парсер завершил работу'
NOTHING_FIND_MESSAGE = 'Ничего не нашлось'
PARSER_LAUNCHED_MESSAGE = 'Парсер запущен!'
MISMATCHED_STATUS = ("Несовпадающий статус:\n"
                     "{}\n"
                     "Статус в карточке: {}\n"
                     "Ожидаемые статусы: {}")
COMMAND_LINE_ARGUMENTS = 'Аргументы командной строки: {}'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    log_messages = []
    for section in tqdm(sections_by_python):
        version_link = urljoin(
            whats_new_url,
            find_tag(section, 'a')['href']
        )
        try:
            soup = get_soup(session, version_link)
            results.append(
                (
                    version_link,
                    find_tag(soup, 'h1').text,
                    find_tag(soup, 'dl').text.replace('\n', ' ')
                )
            )
        except ConnectionError as error:
            log_messages.append(ERROR_MESSAGE.format(error))
    list(map(logging.error, log_messages))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    ul_tags = find_tag(
        soup, 'div', attrs={'class': 'sphinxsidebarwrapper'}
    ).find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise NothingFindException(NOTHING_FIND_MESSAGE)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version = a_tag.text
            status = ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    archive_url = urljoin(
        downloads_url,
        soup.select_one(
            'div[role="main"] table.docutils a[href*="pdf-a4.zip"]')['href']
    )
    downloads_dir = BASE_DIR / DOWNLOAD_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(session.get(archive_url).content)
    logging.info(ARCHIVE_UPLOADED_MESSAGE.format(archive_path))


def pep(session):
    def get_pep_status(link):
        soup = get_soup(session, link)
        if soup is not None:
            status_element = None
            for dt_tag in soup.find_all('dt'):
                if dt_tag.get_text(strip=True) == 'Status:':
                    status_element = dt_tag
            if status_element is not None:
                return status_element.find_next_sibling('dd').text

    soup = get_soup(session, PEP_URL)
    pep_tables = soup.find_all(
        'table',
        {'class': 'pep-zero-table docutils align-default'}
    )
    pep_statuses = defaultdict(int)
    pep_urls = set()
    log_messages = []
    for table in tqdm(pep_tables, desc='Таблицы с PEP'):
        for row in find_tag(table, 'tbody').find_all('tr'):
            preview_status = EXPECTED_STATUS.get(row.contents[0].text[1:], '')
            url = urljoin(PEP_URL, row.contents[2].find('a')['href'])
            pep_status = get_pep_status(url)
            if pep_status not in preview_status:
                log_messages.append(MISMATCHED_STATUS.format(
                    url, pep_status, preview_status
                ))
            if url not in pep_urls:
                pep_statuses[pep_status] += 1
                pep_urls.add(url)
    list(map(logging.error, log_messages))
    return [
        ('Статус', 'Количество'),
        *pep_statuses.items(),
        ('Всего', sum(pep_statuses.values()))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(PARSER_LAUNCHED_MESSAGE)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(COMMAND_LINE_ARGUMENTS.format(args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.error(ERROR_MESSAGE.format(error))
    logging.info(FINISH_WORK_MESSAGE)


if __name__ == '__main__':
    main()
