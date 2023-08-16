import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (ARCHIVE_UPLOADED_MESSAGE, BASE_DIR,
                       COMMAND_LINE_ARGUMENTS, EXPECTED_STATUS,
                       FINISH_WORK_MESSAGE, MAIN_DOC_URL,
                       MISMATCHED_STATUS, NOTHING_FIND_MESSAGE,
                       PARSER_LAUNCHED_MESSAGE, PEP_URL)

from exceptions import NothingFindException
from outputs import control_output
from utils import find_tag, get_response, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(get_response(session, whats_new_url))
    sections_by_python = find_tag(
        find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'}),
        'div',
        attrs={'class': 'toctree-wrapper'}
    ).find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(
            whats_new_url,
            find_tag(section, 'a')['href']
        )
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = get_soup(response)
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )
    return results


def latest_versions(session):
    soup = get_soup(get_response(session, MAIN_DOC_URL))
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
    soup = get_soup(get_response(session, downloads_url))
    arhive_url = urljoin(
        downloads_url,
        find_tag(
            find_tag(
                find_tag(soup, 'div', {'role': 'main'}),
                'table', {'class': 'docutils'}),
            'a',
            {'href': re.compile(r'.+pdf-a4\.zip$')}
        )['href']
    )
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / arhive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(session.get(arhive_url).content)
    logging.info(ARCHIVE_UPLOADED_MESSAGE.format(archive_path))


def get_pep_status(session, link):
    status_element = None
    for dt_tag in get_soup(get_response(session, link)).find_all('dt'):
        if dt_tag.get_text(strip=True) == 'Status:':
            status_element = dt_tag
    if status_element is not None:
        return status_element.find_next_sibling('dd').text


def pep(session):
    soup = get_soup(get_response(session, PEP_URL))
    pep_tables = soup.find_all(
        'table',
        {'class': 'pep-zero-table docutils align-default'}
    )
    result = [('Статус', 'Количество')]
    pep_urls = dict()
    for table in tqdm(pep_tables, desc='Таблицы с PEP'):
        for row in find_tag(table, 'tbody').find_all('tr'):
            preview_status = EXPECTED_STATUS.get(row.contents[0].text[1:], '')
            url = urljoin(PEP_URL, row.contents[2].find('a')['href'])
            pep_status = get_pep_status(session, url)
            if pep_status not in preview_status:
                logging.info(MISMATCHED_STATUS.format(
                    url, pep_status, preview_status
                ))
            if url not in pep_urls:
                pep_urls[url] = {'status': pep_status, 'amount': 1}
            else:
                pep_urls[url]['status'] = pep_status
    statuses = dict()
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
    logging.info(PARSER_LAUNCHED_MESSAGE)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(COMMAND_LINE_ARGUMENTS.format(args))
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    results = MODE_TO_FUNCTION[args.mode](session)
    if results is not None:
        control_output(results, args)
    logging.info(FINISH_WORK_MESSAGE)


if __name__ == '__main__':
    main()
