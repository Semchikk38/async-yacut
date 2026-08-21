import re

SHORT_MAX_LENGTH = 16
ORIGINAL_MAX_LENGTH = 2048

SHORT_ID_REGEX = re.compile(r'^[A-Za-z0-9]+$')

EXTRACT_SHORT_ID_FUNC = 'get_by_short'
EXTRACT_ORIGINAL_FUNC = 'get_by_original'

MSG_EMPTY_BODY = 'Отсутствует тело запроса'
MSG_NO_URL = '"url" является обязательным полем!'
MSG_INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
MSG_ALREADY_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
MSG_NOT_FOUND = 'Указанный id не найден'
