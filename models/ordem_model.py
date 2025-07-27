# -*- coding: utf-8 -*-
"""
SEMAPA3 - OrdemServico Model
Modelo para gerenciamento de ordens de serviço
"""

from core.database import db, BaseModel
from datetime import datetime

class OrdemServico(BaseModel):
    """Modelo de ordem de serviço"""
    __tablename__ = 'ordens_servico'

    numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    requerimento_id = db.Column(db.Integer, db.ForeignKey('requerimentos.id'), nullable=False)
    descricao_servico = db.Column(db.Text, nullable=False)
    data_programada = db.Column(db.Date)
    data_execucao = db.Column(db.Date)
    status = db.Column(db.String(20), default='pendente')  # pendente, em_andamento, concluida, cancelada
    observacoes = db.Column(db.Text)
    custo_estimado = db.Column(db.Float)
    custo_real = db.Column(db.Float)

    # Relacionamentos
    vistorias = db.relationship('Vistoria', backref='ordem_servico', lazy=True)

    def __init__(self, numero, requerimento_id, descricao_servico, data_programada=None, 
                 custo_estimado=None, observacoes=None):
        self.numero = numero
        self.requerimento_id = requerimento_id
        self.descricao_servico = descricao_servico
        self.data_programada = data_programada
        self.custo_estimado = custo_estimado
        self.observacoes = observacoes

    @classmethod
    def generate_numero(cls):
        """Gera número sequencial para ordem de serviço"""
        last_ordem = cls.query.order_by(cls.id.desc()).first()
        if last_ordem:
            last_num = int(last_ordem.numero.split('/')[-1])
            return f"OS/{datetime.now().year}/{last_num + 1:04d}"
        return f"OS/{datetime.now().year}/0001"

    @classmethod
    def get_by_status(cls, status):
        """Retorna ordens por status"""
        return cls.query.filter_by(status=status).order_by(cls.data_programada).all()

    @classmethod
    def get_programadas_hoje(cls):
        """Retorna ordens programadas para hoje"""
        hoje = datetime.now().date()
        return cls.query.filter_by(data_programada=hoje, status='pendente').all()

    def iniciar(self):
        """Inicia execução da ordem"""
        self.status = 'em_andamento'
        self.save()

    def concluir(self, custo_real=None):
        """Conclui a ordem de serviço"""
        self.status = 'concluida'
        self.data_execucao = datetime.now().date()
        if custo_real:
            self.custo_real = custo_real
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
    def dias_atraso(self):
        """Retorna dias de atraso se aplicável"""
        if self.data_programada and self.status in ['pendente', 'em_andamento']:
            hoje = datetime.now().date()
            if hoje > self.data_programada:
                return (hoje - self.data_programada).days
        return 0

    def __repr__(self):
        return f'<OrdemServico {self.numero}>'
