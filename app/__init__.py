from flask import Flask

from app.config import Config


def create_app(config=None):
    # create and configure the app
    app = Flask(__name__)

    if config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    from app.database import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from app.auth import loginManager

    loginManager.init_app(app)
    loginManager.login_view = "auth.login"

    from app.auth.views import bp as auth_bp

    app.register_blueprint(auth_bp)

    from app.index.views import bp as index_bp

    app.register_blueprint(index_bp)

    from app.cli import database

    app.cli.add_command(database.cli, "database")

    return app
