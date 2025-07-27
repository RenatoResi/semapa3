# -*- coding: utf-8 -*-
"""
SEMAPA3 - Core Security
Configurações de segurança, autenticação e autorização
"""

from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from flask import abort, current_app
from werkzeug.security import generate_password_hash, check_password_hash

# Instâncias globais
login_manager = LoginManager()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para Flask-Login"""
    from models.user_model import User
    return User.query.get(int(user_id))

def require_role(role):
    """Decorator para verificar nível de acesso do usuário"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            if not current_user.is_authenticated:
                return login_manager.unauthorized()

            role_hierarchy = {
                'user': 1,
                'tecnico': 2,
                'admin': 3,
                'super_admin': 4
            }

            required_level = role_hierarchy.get(role, 0)
            user_level = role_hierarchy.get(current_user.nivel, 0)

            if user_level < required_level:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

class SecurityMixin:
    """Mixin para funcionalidades de segurança em modelos"""

    @staticmethod
    def hash_password(password):
        """Gera hash da senha"""
        return generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha, password)

    def is_admin(self):
        """Verifica se o usuário é admin"""
        return self.nivel in ['admin', 'super_admin']

    def is_tecnico(self):
        """Verifica se o usuário é técnico ou superior"""
        return self.nivel in ['tecnico', 'admin', 'super_admin']
