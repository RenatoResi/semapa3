# -*- coding: utf-8 -*-
"""
SEMAPA3 - OrdemServico Model
Modelo de ordem de serviço ajustado conforme DDL da tabela ordens_servico
"""

from core.database import db, BaseModel
from datetime import datetime


class OrdemServico(BaseModel):
    """Modelo de ordem de serviço"""
    __tablename__ = 'ordens_servico'

    numero = db.Column(db.String(20), unique=True, nullable=True, index=True)
    data_emissao = db.Column(db.DateTime, nullable=True)
    data_execucao = db.Column(db.DateTime, nullable=True)
    responsavel = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    criado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    data_atualizacao = db.Column(db.DateTime, nullable=True)
    atualizado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relacionamento many-to-many com Requerimento
    requerimentos = db.relationship(
        'Requerimento',
        secondary='ordem_servico_requerimento',
        back_populates='ordens_servico',
        lazy=True
    )

    def __init__(self, numero=None, data_emissao=None, responsavel=None, status='pendente',
                 observacao=None, criado_por=None):
        self.numero = numero
        self.data_emissao = data_emissao or datetime.utcnow()
        self.responsavel = responsavel
        self.status = status
        self.observacao = observacao
        self.criado_por = criado_por

    @classmethod
    def generate_numero(cls):
        """Gera número sequencial para ordem de serviço"""
        last_ordem = cls.query.order_by(cls.id.desc()).first()
        if last_ordem and last_ordem.numero:
            try:
                last_num = int(last_ordem.numero.split('/')[-1])
                return f"OS/{datetime.now().year}/{last_num + 1:04d}"
            except Exception:
                return f"OS/{datetime.now().year}/0001"
        return f"OS/{datetime.now().year}/0001"

    @classmethod
    def get_by_status(cls, status):
        """Retorna ordens por status"""
        return cls.query.filter_by(status=status).order_by(cls.data_emissao.desc()).all()

    @classmethod
    def get_by_responsavel(cls, responsavel):
        """Retorna ordens por responsável"""
        return cls.query.filter_by(responsavel=responsavel).order_by(cls.data_emissao.desc()).all()

    def iniciar(self):
        """Inicia execução da ordem"""
        self.status = 'em_andamento'
        self.save()

    def concluir(self):
        """Conclui a ordem de serviço"""
        self.status = 'concluida'
        self.data_execucao = datetime.utcnow()
        self.save()

    def cancelar(self):
        """Cancela a ordem de serviço"""
        self.status = 'cancelada'
        self.save()

    @property
    def pode_editar(self):
        """Verifica se a ordem pode ser editada"""
        return self.status in ['pendente', 'em_andamento']

    @property
    def total_requerimentos(self):
        """Retorna total de requerimentos vinculados"""
        return len(self.requerimentos)

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['total_requerimentos'] = self.total_requerimentos
        data['pode_editar'] = self.pode_editar
        return data

    def __repr__(self):
        return f'<OrdemServico {self.numero}>'
