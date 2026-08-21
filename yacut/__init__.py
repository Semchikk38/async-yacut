from flask import Flask
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
    from .api_views import api
    app.register_blueprint(main)
    app.register_blueprint(api)

    from .errors import register_error_handlers
    register_error_handlers(app)

    return app


app = create_app()
