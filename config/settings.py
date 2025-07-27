# -*- coding: utf-8 -*-
"""
SEMAPA3 - Configurações da Aplicação
Centralizando todas as configurações do sistema
"""

import os
from pathlib import Path

class Config:
    """Configurações base da aplicação"""

    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'semapa3-secret-key-development'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Database
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_PATH = BASE_DIR / 'semapa.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Faça login para acessar esta página.'
    LOGIN_MESSAGE_CATEGORY = 'info'

    # Upload de arquivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # Paginação
    ITEMS_PER_PAGE = 10

    # Flask-WTF
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora

    # Server
    HOST = '0.0.0.0'
    PORT = 5000

    @staticmethod
    def init_app(app):
        """Inicialização específica da configuração"""
        # Criar diretório de uploads se não existir
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Log para arquivo em produção
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug:
            file_handler = RotatingFileHandler('logs/semapa3.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('SEMAPA3 startup')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
