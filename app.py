# -*- coding: utf-8 -*-
"""
SEMAPA3 - Application Factory
Configuração principal da aplicação Flask usando Factory Pattern
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from core.database import db
from core.security import login_manager, csrf
from core.exceptions import register_error_handlers

def create_app(config_class):
    """Factory para criar instância da aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Registrar error handlers
    register_error_handlers(app)

    # Registrar blueprints
    from controllers.auth_controller import auth_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.requerente_controller import requerente_bp
    from controllers.arvore_controller import arvore_bp
    from controllers.especie_controller import especie_bp
    from controllers.requerimento_controller import requerimento_bp
    from controllers.ordem_servico_controller import ordem_servico_bp
    from controllers.vistoria_controller import vistoria_bp
    from controllers.api_controller import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(requerente_bp)
    app.register_blueprint(arvore_bp)
    app.register_blueprint(especie_bp)
    app.register_blueprint(requerimento_bp)
    app.register_blueprint(ordem_servico_bp)
    app.register_blueprint(vistoria_bp)
    app.register_blueprint(api_bp)

    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()

    return app
