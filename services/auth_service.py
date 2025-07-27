# -*- coding: utf-8 -*-
"""
SEMAPA3 - Auth Service
Serviço de autenticação e autorização
"""

from models.user_model import User
from core.exceptions import ValidationError, UnauthorizedError
import re

class AuthService:
    """Serviço de autenticação"""

    @staticmethod
    def login(email, password):
        """Realiza login do usuário"""
        if not email or not password:
            raise ValidationError("Email e senha são obrigatórios")

        # Validar formato do email
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError("Formato de email inválido")

        user = User.authenticate(email, password)
        if not user:
            raise UnauthorizedError("Email ou senha incorretos")

        user.update_last_login()
        return user

    @staticmethod
    def register(nome, email, senha, nivel='user'):
        """Registra novo usuário"""
        if not all([nome, email, senha]):
            raise ValidationError("Nome, email e senha são obrigatórios")

        # Validar se email já existe
        if User.find_by_email(email):
            raise ValidationError("Email já cadastrado")

        # Validar força da senha
        if len(senha) < 6:
            raise ValidationError("Senha deve ter pelo menos 6 caracteres")

        user = User(nome=nome, email=email, senha=senha, nivel=nivel)
        return user.save()

    @staticmethod
    def change_password(user, current_password, new_password):
        """Altera senha do usuário"""
        if not user.check_password(current_password):
            raise ValidationError("Senha atual incorreta")

        if len(new_password) < 6:
            raise ValidationError("Nova senha deve ter pelo menos 6 caracteres")

        user.senha = user.hash_password(new_password)
        return user.save()

    @staticmethod
    def reset_password(email):
        """Inicia processo de reset de senha"""
        user = User.find_by_email(email)
        if not user:
            raise ValidationError("Email não encontrado")

        # Aqui implementaria lógica de envio de email
        # Por simplicidade, retornamos apenas sucesso
        return True
