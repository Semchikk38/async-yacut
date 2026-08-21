from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from . import models  # noqa
        db.create_all()

    from .views import main
    from .api_views import api, InvalidAPIUsage
    app.register_blueprint(main)
    app.register_blueprint(api)

    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Ресурс не найден'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(InvalidAPIUsage)
    def handle_invalid_usage(error):
        response = jsonify({'message': error.message})
        response.status_code = error.status_code
        return response

    return app


app = create_app()
