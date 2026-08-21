from http import HTTPStatus

from flask import jsonify, render_template, request


class InvalidAPIUsage(Exception):
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Ресурс не найден'}), HTTPStatus.NOT_FOUND
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND


def internal_error(e):
    from . import db
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': 'Внутренняя ошибка сервера'}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    return render_template('errors/500.html'), HTTPStatus.INTERNAL_SERVER_ERROR


def handle_invalid_api_usage(error):
    response = jsonify({'message': error.message})
    response.status_code = error.status_code
    return response


def register_error_handlers(app):
    app.errorhandler(HTTPStatus.NOT_FOUND)(page_not_found)
    app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)(internal_error)
    app.errorhandler(InvalidAPIUsage)(handle_invalid_api_usage)
