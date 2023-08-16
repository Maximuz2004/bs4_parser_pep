class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class NothingFindException(Exception):
    """Вызывается, когда парсер не нашел нужную информацию"""
    pass
