from http import HTTPStatus

from flask import Blueprint, request, jsonify

from .constants import (
    MSG_EMPTY_BODY,
    MSG_NO_URL,
    MSG_INVALID_SHORT,
    MSG_ALREADY_EXISTS,
    MSG_NOT_FOUND,
    SHORT_MAX_LENGTH,
    SHORT_ID_PATTERN,
)
from .models import URLMap

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': MSG_EMPTY_BODY}), HTTPStatus.BAD_REQUEST
    if 'url' not in data:
        return jsonify({'message': MSG_NO_URL}), HTTPStatus.BAD_REQUEST

    custom = data.get('custom_id')
    if custom == '':
        custom = None

    if custom:
        if (not SHORT_ID_PATTERN.match(custom)
                or len(custom) > SHORT_MAX_LENGTH):
            return jsonify(
                {'message': MSG_INVALID_SHORT}), HTTPStatus.BAD_REQUEST
        if URLMap.get_by_short(custom) or custom.lower() == 'files':
            return jsonify(
                {'message': MSG_ALREADY_EXISTS}), HTTPStatus.BAD_REQUEST
        short = custom
    else:
        short = URLMap.generate_unique_short()

    url_map = URLMap.create(original=data['url'], short=short)
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@api.route('/id/<short>/', methods=['GET'])
def get_original(short):
    url_map = URLMap.get_by_short(short)
    if not url_map:
        return jsonify({'message': MSG_NOT_FOUND}), HTTPStatus.NOT_FOUND
    return jsonify({'url': url_map.original}), HTTPStatus.OK