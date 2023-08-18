from bs4 import BeautifulSoup

from exceptions import ParserFindTagException

REQUEST_ERROR_MESSAGE = 'Возникла ошибка {} при загрузке страницы {}'
TAG_ERROR_MESSAGE = 'Не найден тег {} {}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except Exception as error:
        raise ConnectionError(REQUEST_ERROR_MESSAGE.format(error, url))


def get_soup(session, url, features='lxml'):
    return BeautifulSoup(get_response(session, url).text, features=features)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=attrs if attrs is not None else {})
    if searched_tag is None:
        raise ParserFindTagException(TAG_ERROR_MESSAGE.format(tag, attrs))
    return searched_tag
