import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv('.env')

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Создает Flask приложение."""
    app = Flask(__name__, template_folder='../templates',
                static_folder='../static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URI', 'sqlite:///db.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from yacut import views, api_views
    app.register_blueprint(views.bp)
    app.register_blueprint(api_views.api_bp)

    from yacut.helpers import register_error_handlers
    register_error_handlers(app)

    return app


app = create_app()
