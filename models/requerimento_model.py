# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerimento Model
Modelo para gerenciamento de requerimentos
"""

from core.database import db, BaseModel
from datetime import datetime

class Requerimento(BaseModel):
    """Modelo de requerimento"""
    __tablename__ = 'requerimentos'

    numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    requerente_id = db.Column(db.Integer, db.ForeignKey('requerentes.id'), nullable=False)
    arvore_id = db.Column(db.Integer, db.ForeignKey('arvores.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # poda, remocao, transplante
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, negado, concluido
    data_requerimento = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    observacoes = db.Column(db.Text)

    # Relacionamentos
    ordens_servico = db.relationship('OrdemServico', backref='requerimento', lazy=True, cascade='all, delete-orphan')

    def __init__(self, numero, requerente_id, arvore_id, usuario_id, tipo, descricao, observacoes=None):
        self.numero = numero
        self.requerente_id = requerente_id
        self.arvore_id = arvore_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.descricao = descricao
        self.observacoes = observacoes

    @classmethod
    def generate_numero(cls):
        """Gera número sequencial para requerimento"""
        last_req = cls.query.order_by(cls.id.desc()).first()
        if last_req:
            last_num = int(last_req.numero.split('/')[-1])
            return f"REQ/{datetime.now().year}/{last_num + 1:04d}"
        return f"REQ/{datetime.now().year}/0001"

    @classmethod
    def get_by_status(cls, status):
        """Retorna requerimentos por status"""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()

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
