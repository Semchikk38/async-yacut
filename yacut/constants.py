import re
import string

SHORT_LENGTH = 6
SHORT_MAX_LENGTH = 16
ORIGINAL_MAX_LENGTH = 2048
MAX_ATTEMPTS = 10
ALLOWED_CHARS = string.ascii_letters + string.digits
SHORT_PATTERN = re.compile(rf'^[{re.escape(ALLOWED_CHARS)}]+$')

FORBIDDEN_SHORT = 'files'

EMPTY_BODY = 'Отсутствует тело запроса'
NO_URL = '"url" является обязательным полем!'
INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
ALREADY_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
NOT_FOUND = 'Указанный id не найден'
INVALID_SHORT_FORM = 'Только латинские буквы и цифры'

REDIRECT_ENDPOINT = 'redirect_short'
REDIRECT_URL_FUNC = 'main.redirect_short'
