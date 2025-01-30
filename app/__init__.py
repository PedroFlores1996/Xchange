from flask import Flask

from app.config import Config

def create_app(config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    from app.models import db
    db.init_app(app)

    from app.auth import loginManager, bp as auth_bp
    loginManager.init_app(app)
    loginManager.login_view = 'auth.login'
    app.register_blueprint(auth_bp)

    from app.index import bp as index_bp
    app.register_blueprint(index_bp)

    return app