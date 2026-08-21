# YaCut — сервис укорачивания ссылок

## Автор
**Ерошевич Семён**  
GitHub: [https://github.com/Semchikk38](https://github.com/Semchikk38)

## Описание
YaCut — Flask-приложение для генерации коротких ссылок, а также для
асинхронной загрузки файлов на Яндекс.Диск с созданием коротких ссылок
на скачивание.

## Технологический стек
- Python 3.9+
- Flask 3.x
- Flask-SQLAlchemy
- Flask-WTF
- SQLite
- aiohttp (асинхронные запросы к Яндекс.Диску)
- Jinja2 (шаблоны)
- pytest (тестирование)

### Как запустить проект Yacut:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone 
```

```
cd yacut
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать в директории проекта файл .env с четыремя переменными окружения:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=your_secret_key
DB=sqlite:///db.sqlite3
```

Создать базу данных и применить миграции:

```
flask db upgrade
```

Запустить проект:

```
flask run
```
