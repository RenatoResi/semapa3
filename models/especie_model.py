# -*- coding: utf-8 -*-
"""
SEMAPA3 - Especie Model
Modelo para gerenciamento de espécies de árvores
"""

from core.database import db, BaseModel

class Especie(BaseModel):
    """Modelo de espécie de árvore"""
    __tablename__ = 'especies'

    nome_cientifico = db.Column(db.String(100), nullable=False, unique=True, index=True)
    nome_popular = db.Column(db.String(100), nullable=False, index=True)
    familia = db.Column(db.String(50))
    origem = db.Column(db.String(20))  # 'nativa' ou 'exotica'
    porte = db.Column(db.String(20))   # 'pequeno', 'medio', 'grande'
    observacoes = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True, nullable=False)

    # Relacionamentos
    arvores = db.relationship('Arvore', backref='especie', lazy=True)

    def __init__(self, nome_cientifico, nome_popular, familia=None, origem=None, porte=None, observacoes=None):
        self.nome_cientifico = nome_cientifico
        self.nome_popular = nome_popular
        self.familia = familia
        self.origem = origem
        self.porte = porte
        self.observacoes = observacoes

    @classmethod
    def get_active(cls):
        """Retorna apenas espécies ativas"""
        return cls.query.filter_by(ativa=True).order_by(cls.nome_popular).all()

    @classmethod
    def search(cls, query):
        """Busca espécies por nome científico ou popular"""
        from sqlalchemy import or_
        return cls.query.filter(
            or_(
                cls.nome_cientifico.contains(query),
                cls.nome_popular.contains(query)
            )
        ).filter_by(ativa=True).all()

    @property
    def total_arvores(self):
        """Retorna total de árvores desta espécie"""
        return len(self.arvores)

    def __repr__(self):
        return f'<Especie {self.nome_popular}>'
