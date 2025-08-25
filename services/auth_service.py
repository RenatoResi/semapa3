# -*- coding: utf-8 -*-
"""
SEMAPA3 - Auth Service CORRECTED
Serviço de autenticação e autorização - CORRIGIDO
"""

from models.user_model import User
from core.exceptions import ValidationError, UnauthorizedError
from core.database import db
import re

class AuthService:
    """Serviço de autenticação - CORRIGIDO"""

    @staticmethod
    def login(email, password):
        """Realiza login do usuário - CORRIGIDO"""
        if not email or not password:
            raise ValidationError("Email e senha são obrigatórios")

        # Validar formato do email
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError("Formato de email inválido")

        # CORRIGIDO: Usar método authenticate da classe User
        user = User.authenticate(email, password)
        if not user:
            raise UnauthorizedError("Email ou senha incorretos")

        return user

    @staticmethod
    def register(nome, email, senha, nivel='user'):
        """Registra novo usuário - CORRIGIDO"""
        if not all([nome, email, senha]):
            raise ValidationError("Nome, email e senha são obrigatórios")

        # Validar se email já existe
        if User.find_by_email(email):
            raise ValidationError("Email já cadastrado")

        # Validar força da senha
        if len(senha) < 6:
            raise ValidationError("Senha deve ter pelo menos 6 caracteres")

        # Converter nível de string para int se necessário
        nivel_map = {
            'user': 1,
            'tecnico': 2,
            'admin': 3,
            'super_admin': 4
        }
        
        if isinstance(nivel, str):
            nivel = nivel_map.get(nivel, 4)  # Default para admin normal

        # CORRIGIDO: Criar usuário com senha que será hasheada no __init__
        try:
            user = User(
                email=email,
                password=senha,  # Será hasheada no __init__ do User
                nome=nome,
                nivel=nivel,
                ativo=True
            )
            
            db.session.add(user)
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"Erro ao criar usuário: {str(e)}")

    @staticmethod
    def change_password(user, current_password, new_password):
        """Altera senha do usuário - CORRIGIDO"""
        if not user.check_password(current_password):
            raise ValidationError("Senha atual incorreta")

        if len(new_password) < 6:
            raise ValidationError("Nova senha deve ter pelo menos 6 caracteres")

        try:
            # CORRIGIDO: Usar método set_password que hasheia a senha
            user.set_password(new_password)
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"Erro ao alterar senha: {str(e)}")

    @staticmethod
    def reset_password(email):
        """Inicia processo de reset de senha"""
        user = User.find_by_email(email)
        if not user:
            raise ValidationError("Email não encontrado")

        # Aqui implementaria lógica de envio de email
        # Por simplicidade, retornamos apenas sucesso
        return True
    
    @staticmethod
    def create_default_admin():
        """NOVO: Cria usuário admin padrão se não existir"""
        try:
            admin = User.query.filter_by(email='admin@semapa.gov.br').first()
            if not admin:
                admin = User(
                    email='admin@semapa.gov.br',
                    password='123456',  # Será hasheada no __init__
                    nome='Administrador',
                    nivel=4,  # Super admin
                    ativo=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin padrão criado (admin@semapa.gov.br / 123456)")
                return admin
            else:
                print("✅ Usuário admin já existe")
                return admin
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar admin padrão: {e}")
            raise