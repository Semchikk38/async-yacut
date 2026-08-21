import datetime
import secrets

from flask import url_for

from . import db
from .constants import (
    ORIGINAL_MAX_LENGTH,
    SHORT_MAX_LENGTH,
    SHORT_LENGTH,
    MAX_ATTEMPTS,
    ALLOWED_CHARS,
    FORBIDDEN_SHORT,
    REDIRECT_ENDPOINT,
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_MAX_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create(original, short=None):
        if short is None:
            short = URLMap.generate_unique_short()
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def generate_unique_short():
        for _ in range(MAX_ATTEMPTS):
            short = ''.join(
                secrets.choice(ALLOWED_CHARS) for _ in range(SHORT_LENGTH)
            )
            if short != FORBIDDEN_SHORT and not URLMap.get(short):
                return short
        raise RuntimeError(
            'Не удалось сгенерировать уникальную ссылку '
            f'за {MAX_ATTEMPTS} попыток'
        )

    def get_short_url(self):
        return url_for(REDIRECT_ENDPOINT, short=self.short, _external=True)
