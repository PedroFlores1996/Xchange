from flask import Flask
from flask_migrate import Migrate

from app.config import Config


def create_app(config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    from app.database import db

    db.init_app(app)
    app.migrate = Migrate(app, db)

    from app.auth import loginManager

    loginManager.init_app(app)
    loginManager.login_view = "auth.login"

    from app.auth.views import bp as auth_bp

    app.register_blueprint(auth_bp)

    from app.index.views import bp as index_bp

    app.register_blueprint(index_bp)

    from app.cli import database

    app.cli.add_command(database.cli, 'database')

    return app
