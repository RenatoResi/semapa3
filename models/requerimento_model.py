# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerimento Model ajustado para o DDL fornecido
"""

from core.database import db, BaseModel
from datetime import datetime


class Requerimento(BaseModel):
    """Modelo de requerimento"""
    __tablename__ = 'requerimentos'

    numero = db.Column(db.String(20), unique=True, nullable=True, index=True)  # nullable conforme tabela
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

    # Relacionamentos
    ordens_servico = db.relationship('OrdemServico', backref='requerimento', lazy=True, cascade='all, delete-orphan')

    def __init__(self, numero=None, tipo=None, motivo=None, status=None, prioridade=None,
                 requerente_id=None, arvore_id=None, observacao=None,
                 data_abertura=None, data_criacao=None,
                 criado_por=None, data_atualizacao=None, atualizado_por=None):
        self.numero = numero
        self.tipo = tipo
        self.motivo = motivo
        self.status = status
        self.prioridade = prioridade

        self.requerente_id = requerente_id
        self.arvore_id = arvore_id
        self.observacao = observacao

        self.data_abertura = data_abertura
        self.data_criacao = data_criacao or datetime.utcnow()
        self.criado_por = criado_por
        self.data_atualizacao = data_atualizacao
        self.atualizado_por = atualizado_por

    @classmethod
    def generate_numero(cls):
        """Gera número sequencial para requerimento"""
        last_req = cls.query.order_by(cls.id.desc()).first()
        from datetime import datetime
        if last_req and last_req.numero:
            try:
                last_num = int(last_req.numero.split('/')[-1])
                return f"REQ/{datetime.now().year}/{last_num + 1:04d}"
            except Exception:
                # Caso formato não esperado
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
        self.save()

    def negar(self):
        """Nega o requerimento"""
        self.status = 'negado'
        self.save()

    def concluir(self):
        """Conclui o requerimento"""
        self.status = 'concluido'
        self.save()

    @property
    def pode_editar(self):
        """Verifica se o requerimento pode ser editado"""
        return self.status == 'pendente'

    def __repr__(self):
        return f'<Requerimento {self.numero}>'
