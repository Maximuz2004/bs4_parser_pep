import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

REQUEST_ERROR_MESSAGE = 'Возникла ошибка при загрузке страницы {}'
TAG_ERROR_MESSAGE = 'Не найден тег {} {}'


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            REQUEST_ERROR_MESSAGE.format(url),
            stack_info=True
        )


def get_soup(response):
    if response is None:
        return
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = TAG_ERROR_MESSAGE.format(tag, attrs)
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
