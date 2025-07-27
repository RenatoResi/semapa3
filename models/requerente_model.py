# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerente Model
Modelo para gerenciamento de requerentes
"""

from core.database import db, BaseModel
from sqlalchemy import or_

class Requerente(BaseModel):
    """Modelo de requerente"""
    __tablename__ = 'requerentes'

    nome = db.Column(db.String(100), nullable=False, index=True)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=False, index=True)
    tipo = db.Column(db.String(10), nullable=False)  # 'pf' ou 'pj'
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    endereco = db.Column(db.Text)

    # Relacionamentos
    requerimentos = db.relationship('Requerimento', backref='requerente', lazy=True, cascade='all, delete-orphan')

    def __init__(self, nome, cpf_cnpj, tipo, telefone=None, email=None, endereco=None):
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        self.tipo = tipo
        self.telefone = telefone
        self.email = email
        self.endereco = endereco

    @classmethod
    def search(cls, query):
        """Busca requerentes por nome ou CPF/CNPJ"""
        return cls.query.filter(
            or_(
                cls.nome.contains(query),
                cls.cpf_cnpj.contains(query)
            )
        ).all()

    @classmethod
    def find_by_cpf_cnpj(cls, cpf_cnpj):
        """Busca requerente por CPF/CNPJ"""
        return cls.query.filter_by(cpf_cnpj=cpf_cnpj).first()

    @property
    def total_requerimentos(self):
        """Retorna total de requerimentos do requerente"""
        return len(self.requerimentos)

    def __repr__(self):
        return f'<Requerente {self.nome}>'
