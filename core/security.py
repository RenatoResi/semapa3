# -*- coding: utf-8 -*-
"""
SEMAPA3 - Core Security
Sistema de autenticação e autorização com hash de senha
"""

from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from flask import abort
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Instâncias globais
login_manager = LoginManager()
csrf = CSRFProtect()

# Configurações do Flask-Login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário pelo ID"""
    # Import local para evitar importação circular
    from models.user_model import User
    return User.query.get(int(user_id))

def require_role(min_level):
    """Decorator para controle de acesso por nível"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.nivel < min_level:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class SecurityMixin:
    """Mixin para adicionar funcionalidades de segurança aos models"""
    
    def hash_password(self, password):
        """Gera hash da senha"""
        return generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password, password)
    
    def can_edit(self, user):
        """Verifica se usuário pode editar este registro"""
        return user.nivel >= 2 or getattr(self, 'criado_por', None) == user.id
    
    def can_delete(self, user):
        """Verifica se usuário pode deletar este registro"""
        return user.nivel >= 3 or getattr(self, 'criado_por', None) == user.id
