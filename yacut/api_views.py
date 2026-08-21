from http import HTTPStatus

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

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
from .errors import InvalidAPIUsage
from .models import URLMap

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage(EMPTY_BODY)
    if 'url' not in data:
        raise InvalidAPIUsage(NO_URL)

    short = data.get('custom_id')
    if short:
        if not SHORT_PATTERN.match(short) or len(short) > SHORT_MAX_LENGTH:
            raise InvalidAPIUsage(INVALID_SHORT)
        if short == FORBIDDEN_SHORT:
            raise InvalidAPIUsage(ALREADY_EXISTS)
        if URLMap.get(short):
            raise InvalidAPIUsage(ALREADY_EXISTS)
    else:
        short = None

    try:
        url_map = URLMap.create(original=data['url'], short=short)
    except IntegrityError as exc:
        raise InvalidAPIUsage(str(exc))

    return jsonify({
        'url': url_map.original,
        'short_link': url_map.get_short_url()
    }), HTTPStatus.CREATED


@api.route('/id/<short>/', methods=['GET'])
def get_original(short):
    url_map = URLMap.get(short)
    if not url_map:
        raise InvalidAPIUsage(NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
