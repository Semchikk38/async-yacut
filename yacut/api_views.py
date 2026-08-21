from flask import Blueprint, request, jsonify
from .models import URLMap
from .utils import get_unique_short_id, is_valid_short_id
from .constants import (
    SHORT_MAX_LENGTH,
    MSG_EMPTY_BODY,
    MSG_NO_URL,
    MSG_INVALID_SHORT,
    MSG_ALREADY_EXISTS,
    MSG_NOT_FOUND,
)

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': MSG_EMPTY_BODY}), 400
    if 'url' not in data:
        return jsonify({'message': MSG_NO_URL}), 400

    original = data['url']
    custom = data.get('custom_id')

    if custom == '':
        custom = None

    if custom:
        if (not is_valid_short_id(custom)
                or len(custom) > SHORT_MAX_LENGTH):
            return jsonify({'message': MSG_INVALID_SHORT}), 400
        if URLMap.get_by_short(custom) or custom.lower() == 'files':
            return jsonify({'message': MSG_ALREADY_EXISTS}), 400
        short = custom
    else:
        short = get_unique_short_id()

    url_map = URLMap.create(original=original, short=short)

    return jsonify({
        'url': url_map.original,
        'short_link': f'{request.host_url}{url_map.short}',
    }), 201


@api.route('/id/<short_id>/', methods=['GET'])
def get_original(short_id):
    url_map = URLMap.get_by_short(short_id)
    if not url_map:
        return jsonify({'message': MSG_NOT_FOUND}), 404
    return jsonify({'url': url_map.original})