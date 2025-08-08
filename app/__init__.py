from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialiser les extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialiser les extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Enregistrer les blueprints
    from app.routes import public, auth, admin, logistics, distribution
    app.register_blueprint(public.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(logistics.bp, url_prefix='/logistics')
    app.register_blueprint(distribution.bp, url_prefix='/distribution')

    # Créer les tables de la base de données
    with app.app_context():
        db.create_all()

    return app
