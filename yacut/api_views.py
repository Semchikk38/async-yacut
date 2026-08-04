# api_views.py
import re
from flask import Blueprint, request, jsonify
from . import db
from .models import URLMap
from .utils import get_unique_short_id

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        msg = 'Отсутствует тело запроса'
        return jsonify({'message': msg}), 400
    if 'url' not in data:
        msg = '"url" является обязательным полем!'
        return jsonify({'message': msg}), 400

    original = data['url']
    custom = data.get('custom_id')

    if custom:
        if custom == '':
            short = get_unique_short_id()
        else:
            if not re.match(r'^[A-Za-z0-9]+$', custom) or len(custom) > 16:
                msg = 'Указано недопустимое имя для короткой ссылки'
                return jsonify({'message': msg}), 400
            if (URLMap.query.filter_by(short=custom).first()
                    or custom.lower() == 'files'):
                msg = 'Предложенный вариант короткой ссылки уже существует.'
                return jsonify({'message': msg}), 400
            short = custom
    else:
        short = get_unique_short_id()

    url_map = URLMap(original=original, short=short)
    db.session.add(url_map)
    db.session.commit()

    response_data = {
        'url': original,
        'short_link': f'{request.host_url}{short}',
    }
    return jsonify(response_data), 201


@api.route('/id/<short_id>/', methods=['GET'])
def get_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify({'message': 'Указанный id не найден'}), 404
    return jsonify({'url': url_map.original})
