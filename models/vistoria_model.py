# -*- coding: utf-8 -*-
"""
SEMAPA3 - Vistoria Model
Modelo de vistoria ajustado conforme DDL da tabela vistoria
"""

from core.database import db, BaseModel
from datetime import datetime


class Vistoria(BaseModel):
    """Modelo de vistoria técnica"""
    __tablename__ = 'vistoria'

    id = db.Column(db.Integer, primary_key=True)
    requerimento_id = db.Column(db.Integer, db.ForeignKey('requerimentos.id', ondelete='CASCADE'), nullable=False)
    vistoria_data = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Pendente')
    observacoes = db.Column(db.Text, nullable=True)
    especie_id = db.Column(db.Integer, db.ForeignKey('especies.id'), nullable=True)
    condicoes = db.Column(db.Text, nullable=True)
    conflitos = db.Column(db.Text, nullable=True)
    risco_queda = db.Column(db.String(10), nullable=True)
    diagnostico = db.Column(db.Text, nullable=True)
    acao_recomendada = db.Column(db.String(20), nullable=True)
    tipo_poda = db.Column(db.Text, nullable=True)
    galhos_cortar = db.Column(db.Text, nullable=True)
    medidas_seguranca = db.Column(db.Text, nullable=True)
    observacoes_tecnicas = db.Column(db.Text, nullable=True)

    # Relacionamento com fotos
    fotos = db.relationship('VistoriaFoto', backref='vistoria', lazy=True, cascade='all, delete-orphan')

    def __init__(self, requerimento_id, user_id, vistoria_data=None, status='Pendente',
                 observacoes=None, especie_id=None, condicoes=None, conflitos=None,
                 risco_queda=None, diagnostico=None, acao_recomendada=None,
                 tipo_poda=None, galhos_cortar=None, medidas_seguranca=None,
                 observacoes_tecnicas=None):
        self.requerimento_id = requerimento_id
        self.user_id = user_id
        self.vistoria_data = vistoria_data or datetime.utcnow()
        self.status = status
        self.observacoes = observacoes
        self.especie_id = especie_id
        self.condicoes = condicoes
        self.conflitos = conflitos
        self.risco_queda = risco_queda
        self.diagnostico = diagnostico
        self.acao_recomendada = acao_recomendada
        self.tipo_poda = tipo_poda
        self.galhos_cortar = galhos_cortar
        self.medidas_seguranca = medidas_seguranca
        self.observacoes_tecnicas = observacoes_tecnicas

    @classmethod
    def get_by_user(cls, user_id):
        """Retorna vistorias por usuário"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.vistoria_data.desc()).all()

    @classmethod
    def get_by_status(cls, status):
        """Retorna vistorias por status"""
        return cls.query.filter_by(status=status).order_by(cls.vistoria_data.desc()).all()

    @classmethod
    def get_by_periodo(cls, data_inicio, data_fim):
        """Retorna vistorias por período"""
        return cls.query.filter(
            cls.vistoria_data >= data_inicio,
            cls.vistoria_data <= data_fim
        ).order_by(cls.vistoria_data.desc()).all()

    def finalizar(self):
        """Finaliza a vistoria"""
        self.status = 'Finalizada'
        self.save()

    def cancelar(self):
        """Cancela a vistoria"""
        self.status = 'Cancelada'
        self.save()

    @property
    def total_fotos(self):
        """Retorna total de fotos da vistoria"""
        return len(self.fotos)

    @property
    def pode_editar(self):
        """Verifica se a vistoria pode ser editada"""
        return self.status == 'Pendente'

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['total_fotos'] = self.total_fotos
        data['pode_editar'] = self.pode_editar
        return data

    def __repr__(self):
        return f'<Vistoria {self.id} - Req:{self.requerimento_id}>'
