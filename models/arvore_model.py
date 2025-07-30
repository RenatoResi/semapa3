# -*- coding: utf-8 -*-
"""
SEMAPA3 - Arvore Model
Modelo de árvore ajustado conforme DDL da tabela arvores
"""

from core.database import db, BaseModel
from datetime import datetime
from sqlalchemy import or_


class Arvore(BaseModel):
    """Modelo de árvore"""
    __tablename__ = 'arvores'

    endereco = db.Column(db.String(200), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.String(20), nullable=True)  # varchar conforme DDL
    longitude = db.Column(db.String(20), nullable=True)  # varchar conforme DDL
    data_plantio = db.Column(db.DateTime, nullable=True)
    foto = db.Column(db.String(200), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=True)
    criado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    atualizado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    especie_id = db.Column(db.Integer, db.ForeignKey('especies.id'), nullable=True)

    # Relacionamentos
    requerimentos = db.relationship('Requerimento', backref='arvore', lazy=True)

    def __init__(self, endereco=None, bairro=None, latitude=None, longitude=None,
                 data_plantio=None, foto=None, observacao=None, especie_id=None,
                 criado_por=None):
        self.endereco = endereco
        self.bairro = bairro
        self.latitude = latitude
        self.longitude = longitude
        self.data_plantio = data_plantio
        self.foto = foto
        self.observacao = observacao
        self.especie_id = especie_id
        self.data_criacao = datetime.utcnow()
        self.criado_por = criado_por

    @classmethod
    def search(cls, query):
        """Busca árvores por endereço ou bairro"""
        return cls.query.filter(
            or_(
                cls.endereco.contains(query),
                cls.bairro.contains(query)
            )
        ).all()

    @classmethod
    def get_by_bairro(cls, bairro):
        """Retorna árvores por bairro"""
        return cls.query.filter_by(bairro=bairro).all()

    @classmethod  
    def get_by_especie(cls, especie_id):
        """Retorna árvores por espécie"""
        return cls.query.filter_by(especie_id=especie_id).all()

    @property
    def has_coordinates(self):
        """Verifica se a árvore possui coordenadas"""
        return self.latitude is not None and self.longitude is not None

    @property
    def total_requerimentos(self):
        """Retorna total de requerimentos para esta árvore"""
        return len(self.requerimentos)

    @property
    def localizacao_completa(self):
        """Retorna localização completa da árvore"""
        partes = []
        if self.endereco:
            partes.append(self.endereco)
        if self.bairro:
            partes.append(self.bairro)
        return ', '.join(partes) if partes else 'Não informado'

    def get_coordenadas_float(self):
        """Retorna coordenadas como float para uso em mapas"""
        try:
            lat = float(self.latitude) if self.latitude else None
            lng = float(self.longitude) if self.longitude else None
            return lat, lng
        except (ValueError, TypeError):
            return None, None

    def to_kml_dict(self):
        """Converte para dicionário KML"""
        lat, lng = self.get_coordenadas_float()
        return {
            'id': self.id,
            'endereco': self.endereco,
            'bairro': self.bairro,
            'latitude': lat,
            'longitude': lng,
            'especie': self.especie.nome_popular if self.especie else '',
            'observacao': self.observacao
        }

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['total_requerimentos'] = self.total_requerimentos
        data['localizacao_completa'] = self.localizacao_completa
        data['has_coordinates'] = self.has_coordinates
        return data

    def __repr__(self):
        return f'<Arvore {self.id} - {self.localizacao_completa}>'
