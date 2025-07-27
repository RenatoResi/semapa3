# -*- coding: utf-8 -*-
"""
SEMAPA3 - User Model compatível com tabela existente e colunas adicionais
"""

from flask_login import UserMixin
from core.database import db, BaseModel
from core.security import SecurityMixin
from datetime import datetime


class User(BaseModel, UserMixin, SecurityMixin):
    """Modelo de usuário do sistema"""
    __tablename__ = 'users'

    nome = db.Column(db.String(100), nullable=True)  # nullable para não quebrar dados existentes
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    nivel = db.Column(db.Integer, nullable=False, default=3)  # int na tabela, default 3 = usuário normal
    ativo = db.Column(db.Boolean, nullable=True, default=True)  # novo campo
    ultimo_login = db.Column(db.DateTime, nullable=True)       # novo campo

    # Relacionamentos (mantidos iguais)
    vistorias = db.relationship('Vistoria', backref='tecnico', lazy=True)
    requerimentos = db.relationship(
        'Requerimento',
        backref='criador',
        lazy=True,
        foreign_keys='Requerimento.criado_por'
    )
    requerimentos_atualizados = db.relationship(
        'Requerimento',
        backref='atualizador',
        lazy=True,
        foreign_keys='Requerimento.atualizado_por'
    )

    def __init__(self, nome, email, password, telefone=None, nivel=1, ativo=True):
        self.nome = nome
        self.email = email
        self.password = self.hash_password(password)
        self.telefone = telefone
        self.nivel = nivel
        self.ativo = ativo

    def update_last_login(self):
        """Atualiza timestamp do último login"""
        self.ultimo_login = datetime.utcnow()
        self.save()

    def is_active(self):
        """Verifica se o usuário está ativo"""
        return self.ativo if self.ativo is not None else True

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
        if user and user.check_password(password) and user.is_active():
            return user
        return None

    def to_dict(self, include_sensitive=False):
        """Converte para dicionário, excluindo dados sensíveis por padrão"""
        data = super().to_dict()
        if not include_sensitive:
            data.pop('password', None)  # corrigido de 'senha' para 'password'
        return data

    def __repr__(self):
        return f'<User {self.email}>'
