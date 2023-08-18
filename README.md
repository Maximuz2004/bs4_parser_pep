# Парсер PEP с использованием Beautiful Soup


Этот проект представляет собой скрипт на языке Python, использующий библиотеку 
Beautiful Soup для парсинга Python Enhancement Proposals (PEP) с веб-сайта 
Python и извлечения информации о них.

**Стек технологий:**
- [Python 3.9+](https://docs.python.org/3/),
- [requests_cache](https://requests-cache.readthedocs.io/en/stable/),
- [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/),
- [prettytable](https://ptable.readthedocs.io/en/latest/tutorial.html)

## Установка

1. Клонируйте репозиторий:
   ```sh
   git clone https://github.com/Maximuz2004/bs4_parser_pep.git
   ```

2. Перейдите в папку проекта:

   ```sh
    cd bs4_parser_pep
   ```
3. Установите необходимые зависимости:

   ```sh
    pip install -r requirements.txt
   ```

## Использование
Запустите скрипт ```main.py --help```, чтобы узнать режимы работы и возможности
вывода полученной информации.

## Режимы работы:

### whats-new
Получает ссылку на статью версии Python, ее заголовок, информацию о редакторе 
и авторе.

### latest-versions
Получает ссылки на документацию, информацию о версии Python и ее статус
### download
Загружает документацию последней стабильной версии
### pep
Получает информацию по статусам PEP и количество PEP по каждому статусу.

```
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
                        в консоль или в файл
```


Автор: [Титов Максим](https://github.com/Maximuz2004)
