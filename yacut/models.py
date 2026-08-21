import datetime
from . import db
from .constants import SHORT_MAX_LENGTH, ORIGINAL_MAX_LENGTH


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_MAX_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LENGTH), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create(original, short):
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def get_by_short(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def get_by_original(original):
        return URLMap.query.filter_by(original=original).first()