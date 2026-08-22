import datetime
import random

from flask import url_for

from . import db
from .constants import (
    ORIGINAL_MAX_LENGTH,
    SHORT_MAX_LENGTH,
    SHORT_LENGTH,
    MAX_ATTEMPTS,
    ALLOWED_CHARS,
    FORBIDDEN_SHORT,
    REDIRECT_URL_FUNC,
    SHORT_PATTERN,
    INVALID_SHORT,
    ALREADY_EXISTS,
)


class ShortAlreadyExists(Exception):
    def __init__(self):
        super().__init__(ALREADY_EXISTS)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_MAX_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create(original, short=None, validate=True, commit=True):
        if short == '':
            short = None

        if validate:
            if len(original) > ORIGINAL_MAX_LENGTH:
                raise ValueError(
                    f'Длина оригинальной ссылки не должна превышать '
                    f'{ORIGINAL_MAX_LENGTH} символов.'
                )
            if short:
                if len(short
                       ) > SHORT_MAX_LENGTH or not SHORT_PATTERN.match(short):
                    raise ValueError(INVALID_SHORT)
                if short == FORBIDDEN_SHORT or URLMap.get(short):
                    raise ShortAlreadyExists()

        if not short:
            short = URLMap.generate_unique_short()

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        if commit:
            db.session.commit()
        return url_map

    @staticmethod
    def get(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def generate_unique_short():
        for _ in range(MAX_ATTEMPTS):
            short = ''.join(random.choices(ALLOWED_CHARS, k=SHORT_LENGTH))
            if short != FORBIDDEN_SHORT and not URLMap.get(short):
                return short
        raise RuntimeError(
            'Не удалось сгенерировать уникальную короткую ссылку '
            f'после {MAX_ATTEMPTS} попыток.'
        )

    def get_short_url(self):
        return url_for(REDIRECT_URL_FUNC, short=self.short, _external=True)
