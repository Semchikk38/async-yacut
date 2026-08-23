from http import HTTPStatus

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from .constants import EMPTY_BODY, NO_URL, NOT_FOUND, ALREADY_EXISTS
from .errors import InvalidAPIUsage
from .models import URLMap, ShortAlreadyExists

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage(EMPTY_BODY)
    if 'url' not in data:
        raise InvalidAPIUsage(NO_URL)

    short = data.get('custom_id')
    try:
        url_map = URLMap.create(original=data['url'], short=short)
    except (ValueError, ShortAlreadyExists, IntegrityError, RuntimeError
            ) as exc:
        message = exc.args[0] if not isinstance(
            exc, IntegrityError) else ALREADY_EXISTS
        raise InvalidAPIUsage(message)

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
