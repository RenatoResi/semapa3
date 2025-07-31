# -*- coding: utf-8 -*-
"""
SEMAPA3 - User Model
Modelo de usuario ajustado conforme DDL da tabela users
"""
from core.database import db, BaseModel
from flask_login import UserMixin
from core.database import db, BaseModel
from core.security import SecurityMixin
from datetime import datetime


class User(BaseModel, UserMixin, SecurityMixin):
    """Modelo de usuário do sistema"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    nivel = db.Column(db.Integer, nullable=False, default=1)
    ativo = db.Column(db.Boolean, nullable=True, default=True)
    ultimo_login = db.Column(db.DateTime, nullable=True)

    # Relacionamentos com foreign_keys especificadas para evitar ambiguidade
    requerimentos_criados = db.relationship(
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
    
    arvores_criadas = db.relationship(
        'Arvore',
        backref='criador',
        lazy=True,
        foreign_keys='Arvore.criado_por'
    )
    arvores_atualizadas = db.relationship(
        'Arvore',
        backref='atualizador',
        lazy=True,
        foreign_keys='Arvore.atualizado_por'
    )
    
    requerentes_criados = db.relationship(
        'Requerente',
        backref='criador',
        lazy=True,
        foreign_keys='Requerente.criado_por'
    )
    requerentes_atualizados = db.relationship(
        'Requerente',
        backref='atualizador',
        lazy=True,
        foreign_keys='Requerente.atualizado_por'
    )
    
    ordens_criadas = db.relationship(
        'OrdemServico',
        backref='criador',
        lazy=True,
        foreign_keys='OrdemServico.criado_por'
    )
    ordens_atualizadas = db.relationship(
        'OrdemServico',
        backref='atualizador',
        lazy=True,
        foreign_keys='OrdemServico.atualizado_por'
    )
    
    vistorias = db.relationship(
        'Vistoria',
        backref='usuario',
        lazy=True,
        foreign_keys='Vistoria.user_id'
    )

    def __init__(self, email, password, nome=None, telefone=None, nivel=1, ativo=True):
        self.email = email
        self.password = self.hash_password(password)
        self.nome = nome
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
            user.update_last_login()
            return user
        return None

    def to_dict(self, include_sensitive=False):
        """Converte para dicionário, excluindo dados sensíveis por padrão"""
        data = super().to_dict()
        if not include_sensitive:
            data.pop('password', None)
        return data

    def __repr__(self):
        return f'<User {self.email}>'
