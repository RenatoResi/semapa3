# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerente Model
Modelo de requerente ajustado conforme DDL da tabela requerentes
"""

from core.database import db, BaseModel
from datetime import datetime
from sqlalchemy import or_


class Requerente(BaseModel):
    """Modelo de requerente"""
    __tablename__ = 'requerentes'

    nome = db.Column(db.String(100), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=True)
    criado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    atualizado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relacionamentos
    requerimentos = db.relationship('Requerimento', backref='requerente', lazy=True)

    def __init__(self, nome=None, telefone=None, observacao=None, criado_por=None):
        self.nome = nome
        self.telefone = telefone
        self.observacao = observacao
        self.data_criacao = datetime.utcnow()
        self.criado_por = criado_por

    @classmethod
    def search(cls, query):
        """Busca requerentes por nome ou telefone"""
        return cls.query.filter(
            or_(
                cls.nome.contains(query),
                cls.telefone.contains(query)
            )
        ).all()

    @classmethod
    def find_by_telefone(cls, telefone):
        """Busca requerente por telefone"""
        return cls.query.filter_by(telefone=telefone).first()

    @property
    def total_requerimentos(self):
        """Retorna total de requerimentos do requerente"""
        return len(self.requerimentos)

    @property
    def ultimo_requerimento(self):
        """Retorna o requerimento mais recente"""
        if self.requerimentos:
            return max(self.requerimentos, key=lambda r: r.data_criacao or datetime.min)
        return None

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['total_requerimentos'] = self.total_requerimentos
        return data

    def __repr__(self):
        return f'<Requerente {self.nome}>'
