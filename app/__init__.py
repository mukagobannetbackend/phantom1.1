import os
from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'


def normalize_db_url(url: str | None) -> str:
    url = url or 'sqlite:///phantomvault.db'
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif url.startswith('postgresql://') and '+psycopg' not in url:
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates', static_folder='../static')
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-only-change-me'),
        SQLALCHEMY_DATABASE_URI=normalize_db_url(
    os.getenv('DATABASE_URL') or os.getenv('LOCAL_DATABASE_URL')
),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=int(os.getenv('MAX_UPLOAD_MB', '12')) * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('APP_BASE_URL', '').startswith('https://'),
        UPLOAD_FOLDER=str(Path(app.instance_path) / 'uploads'),
    )
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    db.init_app(app); migrate.init_app(app, db); login_manager.init_app(app); csrf.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

 
    from .auth import auth
    from .routes import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    from .coach_routes import coach
    app.register_blueprint(coach)


    @app.context_processor
    def inject_globals():
        return {'app_name': 'PhantomVault Pro'}

    @app.cli.command('init-db')
    def init_db():
        with app.app_context():
            db.create_all()
            print('Database tables created.')

    with app.app_context():
        db.create_all()
    return app
