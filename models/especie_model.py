# -*- coding: utf-8 -*-
"""
SEMAPA3 - Especie Model
Modelo de espécie ajustado conforme DDL da tabela especies
"""

from core.database import db, BaseModel
from sqlalchemy import or_


class Especie(BaseModel):
    """Modelo de espécie de árvore"""
    __tablename__ = 'especies'

    nome_popular = db.Column(db.String(100), nullable=False, unique=True, index=True)
    nome_cientifico = db.Column(db.String(150), nullable=False, index=True)
    porte = db.Column(db.String(20), nullable=False)
    altura_min = db.Column(db.Float, nullable=True)
    altura_max = db.Column(db.Float, nullable=True)
    longevidade_min = db.Column(db.Integer, nullable=True)
    longevidade_max = db.Column(db.Integer, nullable=True)
    deciduidade = db.Column(db.String(30), nullable=True)
    cor_flor = db.Column(db.String(50), nullable=True)
    epoca_floracao = db.Column(db.String(50), nullable=True)
    fruto_comestivel = db.Column(db.String(10), nullable=True)
    epoca_frutificacao = db.Column(db.String(50), nullable=True)
    necessidade_rega = db.Column(db.String(20), nullable=True)
    atrai_fauna = db.Column(db.String(10), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    link_foto = db.Column(db.String(200), nullable=True)

    # Relacionamentos
    arvores = db.relationship('Arvore', backref='especie', lazy=True)
    vistorias = db.relationship('Vistoria', backref='especie', lazy=True)

    def __init__(self, nome_popular, nome_cientifico, porte, altura_min=None, altura_max=None,
                 longevidade_min=None, longevidade_max=None, deciduidade=None, cor_flor=None,
                 epoca_floracao=None, fruto_comestivel=None, epoca_frutificacao=None,
                 necessidade_rega=None, atrai_fauna=None, observacoes=None, link_foto=None):
        self.nome_popular = nome_popular
        self.nome_cientifico = nome_cientifico
        self.porte = porte
        self.altura_min = altura_min
        self.altura_max = altura_max
        self.longevidade_min = longevidade_min
        self.longevidade_max = longevidade_max
        self.deciduidade = deciduidade
        self.cor_flor = cor_flor
        self.epoca_floracao = epoca_floracao
        self.fruto_comestivel = fruto_comestivel
        self.epoca_frutificacao = epoca_frutificacao
        self.necessidade_rega = necessidade_rega
        self.atrai_fauna = atrai_fauna
        self.observacoes = observacoes
        self.link_foto = link_foto

    @classmethod
    def search(cls, query):
        """Busca espécies por nome científico ou popular"""
        return cls.query.filter(
            or_(
                cls.nome_cientifico.contains(query),
                cls.nome_popular.contains(query)
            )
        ).all()

    @classmethod
    def get_by_porte(cls, porte):
        """Retorna espécies por porte"""
        return cls.query.filter_by(porte=porte).order_by(cls.nome_popular).all()

    @property
    def total_arvores(self):
        """Retorna total de árvores desta espécie"""
        return len(self.arvores)

    @property
    def altura_media(self):
        """Retorna altura média se ambos os valores estiverem definidos"""
        if self.altura_min and self.altura_max:
            return (self.altura_min + self.altura_max) / 2
        return self.altura_min or self.altura_max

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['total_arvores'] = self.total_arvores
        data['altura_media'] = self.altura_media
        return data

    def __repr__(self):
        return f'<Especie {self.nome_popular}>'
