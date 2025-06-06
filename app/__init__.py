from flask import Flask

from app.config import Config


def create_app(config=None):
    # create and configure the app
    app = Flask(__name__)

    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    from app.database import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from app.auth import loginManager

    loginManager.init_app(app)
    loginManager.login_view = "auth.login"

    from app.auth.views import bp as auth_bp
    from app.index.views import bp as index_bp
    from app.expense.views import bp as expense_bp
    from app.user.views import bp as user_bp
    from app.group.views import bp as group_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(group_bp)

    from app.cli import database

    app.cli.add_command(database.cli, "database")

    return app
