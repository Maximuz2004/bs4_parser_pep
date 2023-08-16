import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    side_bar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = side_bar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version = a_tag.text
            status = ''
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    arhive_url = urljoin(downloads_url, pdf_a4_link)
    file_name = arhive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / file_name

    response = session.get(arhive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def get_pep_status(session, link):
    response = get_response(session, link)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    status_element = None
    for dt_tag in soup.find_all('dt'):
        if dt_tag.get_text(strip=True) == 'Status:':
            status_element = dt_tag
    if status_element is not None:
        return status_element.find_next_sibling('dd').text


def pep(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    pep_tables = soup.find_all(
        'table',
        {'class': 'pep-zero-table docutils align-default'}
    )
    result = [('Статус', 'Количество')]
    pep_urls = dict()
    for table in tqdm(pep_tables, desc='Таблицы с PEP'):
        table_rows = find_tag(table, 'tbody').find_all('tr')

        for row in table_rows:
            statuses = dict()
            preview_status = EXPECTED_STATUS.get(row.contents[0].text[1:], '')
            url = urljoin(PEP_URL, row.contents[2].find('a')['href'])
            pep_status = get_pep_status(session, url)
            if pep_status not in preview_status:
                logging.info('Несовпадающий статус:')
                logging.info(url)
                logging.info(f'Статус в карточке: {pep_status}')
                logging.info(f'Ожидаемые статусы: {preview_status}')
            if url not in pep_urls:
                pep_urls[url] = {'status': pep_status, 'amount': 1}
            else:
                pep_urls[url]['status'] = pep_status
    for value in pep_urls.values():
        if value['status'] not in statuses:
            statuses[value['status']] = 1
        else:
            statuses[value['status']] += 1
    result.extend((status, amount) for status, amount in statuses.items())
    result.append(('Total', len(pep_urls)))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы коммандной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу')


if __name__ == '__main__':
    main()
