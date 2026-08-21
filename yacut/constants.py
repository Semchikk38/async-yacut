import re

SHORT_LENGTH = 6
SHORT_MAX_LENGTH = 16
ORIGINAL_MAX_LENGTH = 2048
MAX_ATTEMPTS = 10
ALLOWED_CHARS = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
)
SHORT_ID_PATTERN = re.compile(rf'^[{re.escape(ALLOWED_CHARS)}]+$')

MSG_EMPTY_BODY = 'Отсутствует тело запроса'
MSG_NO_URL = '"url" является обязательным полем!'
MSG_INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
MSG_ALREADY_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
MSG_NOT_FOUND = 'Указанный id не найден'
MSG_FILES_FORBIDDEN = 'Имя "files" уже занято.'