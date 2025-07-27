# -*- coding: utf-8 -*-
"""
SEMAPA3 - User Model
Modelo de usuário com autenticação e autorização
"""

from flask_login import UserMixin
from core.database import db, BaseModel
from core.security import SecurityMixin
from datetime import datetime

class User(BaseModel, UserMixin, SecurityMixin):
    """Modelo de usuário do sistema"""
    __tablename__ = 'usuarios'

    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(20), nullable=False, default='user')
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    ultimo_login = db.Column(db.DateTime)

    # Relacionamentos
    requerimentos = db.relationship('Requerimento', backref='usuario', lazy=True)
    vistorias = db.relationship('Vistoria', backref='tecnico', lazy=True)

    def __init__(self, nome, email, senha, nivel='user'):
        self.nome = nome
        self.email = email
        self.senha = self.hash_password(senha)
        self.nivel = nivel

    def update_last_login(self):
        """Atualiza timestamp do último login"""
        self.ultimo_login = datetime.utcnow()
        self.save()

    def is_active(self):
        """Verifica se o usuário está ativo"""
        return self.ativo

    def get_id(self):
        """Retorna ID do usuário para Flask-Login"""
        return str(self.id)

    @classmethod
    def find_by_email(cls, email):
        """Busca usuário por email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def authenticate(cls, email, password):
        """Autentica usuário por email e senha"""
        user = cls.find_by_email(email)
        if user and user.check_password(password) and user.ativo:
            return user
        return None

    def to_dict(self, include_sensitive=False):
        """Converte para dicionário, excluindo dados sensíveis por padrão"""
        data = super().to_dict()
        if not include_sensitive:
            data.pop('senha', None)
        return data

    def __repr__(self):
        return f'<User {self.email}>'
