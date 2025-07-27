# -*- coding: utf-8 -*-
"""
SEMAPA3 - Arvore Model
Modelo para gerenciamento de árvores
"""

from core.database import db, BaseModel
from datetime import datetime

class Arvore(BaseModel):
    """Modelo de árvore"""
    __tablename__ = 'arvores'

    numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    especie_id = db.Column(db.Integer, db.ForeignKey('especies.id'), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    dap = db.Column(db.Float)  # Diâmetro à altura do peito
    altura = db.Column(db.Float)
    estado = db.Column(db.String(20), default='saudavel')  # saudavel, doente, morta, removida
    observacoes = db.Column(db.Text)
    data_plantio = db.Column(db.Date)

    # Relacionamentos
    requerimentos = db.relationship('Requerimento', backref='arvore', lazy=True)
    vistorias = db.relationship('Vistoria', backref='arvore', lazy=True)

    def __init__(self, numero, especie_id, endereco, latitude=None, longitude=None, 
                 dap=None, altura=None, estado='saudavel', observacoes=None, data_plantio=None):
        self.numero = numero
        self.especie_id = especie_id
        self.endereco = endereco
        self.latitude = latitude
        self.longitude = longitude
        self.dap = dap
        self.altura = altura
        self.estado = estado
        self.observacoes = observacoes
        self.data_plantio = data_plantio

    @classmethod
    def find_by_numero(cls, numero):
        """Busca árvore por número"""
        return cls.query.filter_by(numero=numero).first()

    @classmethod
    def search(cls, query):
        """Busca árvores por número ou endereço"""
        from sqlalchemy import or_
        return cls.query.filter(
            or_(
                cls.numero.contains(query),
                cls.endereco.contains(query)
            )
        ).all()

    @classmethod
    def get_by_estado(cls, estado):
        """Retorna árvores por estado"""
        return cls.query.filter_by(estado=estado).all()

    @property
    def has_coordinates(self):
        """Verifica se a árvore possui coordenadas"""
        return self.latitude is not None and self.longitude is not None

    @property
    def total_requerimentos(self):
        """Retorna total de requerimentos para esta árvore"""
        return len(self.requerimentos)

    @property
    def ultima_vistoria(self):
        """Retorna a vistoria mais recente"""
        if self.vistorias:
            return max(self.vistorias, key=lambda v: v.data_vistoria)
        return None

    def to_kml_dict(self):
        """Converte para dicionário KML"""
        return {
            'numero': self.numero,
            'endereco': self.endereco,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'especie': self.especie.nome_popular if self.especie else '',
            'estado': self.estado,
            'dap': self.dap,
            'altura': self.altura
        }

    def __repr__(self):
        return f'<Arvore {self.numero}>'
