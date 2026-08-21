from http import HTTPStatus

from flask import Blueprint, request, jsonify

from .constants import (
    EMPTY_BODY,
    NO_URL,
    INVALID_SHORT,
    ALREADY_EXISTS,
    NOT_FOUND,
    FORBIDDEN_SHORT,
    SHORT_PATTERN,
    SHORT_MAX_LENGTH,
)
from .models import URLMap

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage(EMPTY_BODY, HTTPStatus.BAD_REQUEST)
    if 'url' not in data:
        raise InvalidAPIUsage(NO_URL, HTTPStatus.BAD_REQUEST)

    custom_id = data.get('custom_id')
    if custom_id:
        if not SHORT_PATTERN.match(
                custom_id) or len(custom_id) > SHORT_MAX_LENGTH:
            raise InvalidAPIUsage(INVALID_SHORT, HTTPStatus.BAD_REQUEST)
        if URLMap.get(custom_id) or custom_id == FORBIDDEN_SHORT:
            raise InvalidAPIUsage(ALREADY_EXISTS, HTTPStatus.BAD_REQUEST)
        short = custom_id
    else:
        short = URLMap.generate_unique_short()

    try:
        url_map = URLMap.create(original=data['url'], short=short)
    except Exception:
        raise InvalidAPIUsage('Не удалось создать запись',
                              HTTPStatus.INTERNAL_SERVER_ERROR)
    return jsonify({'url': url_map.original,
                    'short_link': url_map.get_short_url()}), HTTPStatus.CREATED


@api.route('/id/<short>/', methods=['GET'])
def get_original(short):
    url_map = URLMap.get(short)
    if not url_map:
        raise InvalidAPIUsage(NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK


class InvalidAPIUsage(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
