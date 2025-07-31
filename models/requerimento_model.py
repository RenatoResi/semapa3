# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerimento Model
Modelo de requerimento ajustado conforme DDL da tabela requerimentos
"""

from core.database import db, BaseModel
from datetime import datetime


class Requerimento(BaseModel):
    """Modelo de requerimento"""
    __tablename__ = 'requerimentos'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=True, index=True)
    data_abertura = db.Column(db.DateTime, nullable=True)
    tipo = db.Column(db.Text, nullable=True)
    motivo = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=True)
    prioridade = db.Column(db.String(20), nullable=True)
    requerente_id = db.Column(db.Integer, db.ForeignKey('requerentes.id'), nullable=True)
    arvore_id = db.Column(db.Integer, db.ForeignKey('arvores.id'), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=True)
    criado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    atualizado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relacionamento many-to-many com OrdemServico
    ordens_servico = db.relationship(
        'OrdemServico',
        secondary='ordem_servico_requerimento',
        back_populates='requerimentos',
        lazy=True
    )
    
    # Relacionamento com Vistoria
    vistorias = db.relationship('Vistoria', backref='requerimento', lazy=True, cascade='all, delete-orphan')

    def __init__(self, numero=None, tipo=None, motivo=None, status='pendente', prioridade=None,
                 requerente_id=None, arvore_id=None, observacao=None,
                 data_abertura=None, criado_por=None):
        self.numero = numero
        self.tipo = tipo
        self.motivo = motivo
        self.status = status
        self.prioridade = prioridade
        self.requerente_id = requerente_id
        self.arvore_id = arvore_id
        self.observacao = observacao
        self.data_abertura = data_abertura or datetime.utcnow()
        self.data_criacao = datetime.utcnow()
        self.criado_por = criado_por

    @classmethod
    def generate_numero(cls):
        """Gera número sequencial para requerimento"""
        last_req = cls.query.order_by(cls.id.desc()).first()
        if last_req and last_req.numero:
            try:
                last_num = int(last_req.numero.split('/')[-1])
                return f"REQ/{datetime.now().year}/{last_num + 1:04d}"
            except Exception:
                return f"REQ/{datetime.now().year}/0001"
        return f"REQ/{datetime.now().year}/0001"

    @classmethod
    def get_by_status(cls, status):
        """Retorna requerimentos por status"""
        return cls.query.filter_by(status=status).order_by(cls.data_criacao.desc()).all()

    @classmethod
    def search(cls, query):
        """Busca requerimentos por número"""
        return cls.query.filter(cls.numero.contains(query)).all()

    def aprovar(self):
        """Aprova o requerimento"""
        self.status = 'aprovado'
        self.data_atualizacao = datetime.utcnow()
        self.save()

    def negar(self):
        """Nega o requerimento"""
        self.status = 'negado'
        self.data_atualizacao = datetime.utcnow()
        self.save()

    def concluir(self):
        """Conclui o requerimento"""
        self.status = 'concluido'
        self.data_atualizacao = datetime.utcnow()
        self.save()

    @property
    def pode_editar(self):
        """Verifica se o requerimento pode ser editado"""
        return self.status == 'pendente'

    @property
    def total_ordens_servico(self):
        """Retorna total de ordens de serviço vinculadas"""
        return len(self.ordens_servico)

    @property
    def total_vistorias(self):
        """Retorna total de vistorias realizadas"""
        return len(self.vistorias)

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['pode_editar'] = self.pode_editar
        data['total_ordens_servico'] = self.total_ordens_servico
        data['total_vistorias'] = self.total_vistorias
        return data

    def __repr__(self):
        return f'<Requerimento {self.numero}>'
