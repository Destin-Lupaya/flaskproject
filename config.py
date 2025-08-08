import os
from datetime import timedelta

class Config:
    # Clé secrète pour la sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-tres-secrete'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration de la session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Configuration des uploads
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Configuration des rôles
    ROLES = {
        'ADMIN': 'admin',
        'LOGISTICS': 'logistics',
        'FIELD_AGENT': 'field_agent',
        'VIEWER': 'viewer'
    }
    
    # Configuration de l'application
    APP_NAME = "Suivi des Distributions Humanitaires"
    APP_VERSION = "1.0.0"
    
    # Configuration du mail (à compléter selon les besoins)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@example.com']

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
