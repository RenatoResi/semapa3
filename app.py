# -*- coding: utf-8 -*-
"""
SEMAPA3 - Application Factory CORRECTED
Configuração principal da aplicação Flask - CORRIGIDA
"""

from flask import Flask
from core.database import db
from core.security import login_manager, csrf
from core.exceptions import register_error_handlers

def create_app(config_class):
    """Factory para criar instância da aplicação Flask - CORRIGIDA"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Inicializar configurações customizadas (uploads etc)
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    # Registrar error handlers
    register_error_handlers(app)

    # Registrar blueprints
    try:
        # Controllers principais
        from controllers.auth_controller import auth_bp
        from controllers.dashboard_controller import dashboard_bp

        # Controllers de entidades
        from controllers.requerente_controller import requerente_bp
        from controllers.arvore_controller import arvore_bp
        from controllers.especie_controller import especie_bp
        from controllers.requerimento_controller import requerimento_bp
        from controllers.ordem_servico_controller import ordem_servico_bp
        from controllers.vistoria_controller import vistoria_bp

        # API Controller
        from controllers.api_controller import api_bp

        # Registrar todos os blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(requerente_bp)
        app.register_blueprint(arvore_bp)
        app.register_blueprint(especie_bp)
        app.register_blueprint(requerimento_bp)
        app.register_blueprint(ordem_servico_bp)
        app.register_blueprint(vistoria_bp)
        app.register_blueprint(api_bp)

        print("✅ Todos os blueprints registrados com sucesso!")
    except ImportError as e:
        print(f"❌ Erro ao importar blueprint: {e}")
        raise

    # Criar tabelas do banco de dados e usuário admin padrão
    with app.app_context():
        try:
            # Importar todos os models antes de criar as tabelas
            from models import (
                User, Especie, Requerente, Arvore,
                Requerimento, OrdemServico, Vistoria, VistoriaFoto,
                ordem_servico_requerimento
            )
            db.create_all()
            print("✅ Tabelas do banco criadas com sucesso!")
            
            # CORRIGIDO: Usar AuthService para criar admin padrão
            create_default_admin()
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            raise

    return app

def create_default_admin():
    """CORRIGIDO: Usa AuthService para criar usuário administrador padrão"""
    try:
        from services.auth_service import AuthService
        AuthService.create_default_admin()
    except Exception as e:
        print(f"❌ Erro ao criar admin padrão: {e}")