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
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_MAX_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create(original, short=None, validate=False, commit=True):
        if short is None:
            short = URLMap.generate_unique_short()
        elif validate:
            URLMap.validate_original(original)
            URLMap.validate_short(short)
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
            'Не удалось сгенерировать уникальную короткую ссылку.'
        )

    @staticmethod
    def validate_original(original):
        if not original or len(original) > ORIGINAL_MAX_LENGTH:
            raise ValueError('Некорректная оригинальная ссылка')

    @staticmethod
    def validate_short(short):
        if (not SHORT_PATTERN.match(short)
                or len(short) > SHORT_MAX_LENGTH):
            raise ValueError('Некорректная короткая ссылка')

    def get_short_url(self):
        return url_for(REDIRECT_URL_FUNC, short=self.short, _external=True)
