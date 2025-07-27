# -*- coding: utf-8 -*-
"""
SEMAPA3 - Core Database
Configuração do banco de dados usando SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instância global do SQLAlchemy
db = SQLAlchemy()

class BaseModel(db.Model):
    """Modelo base com campos de auditoria"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def save(self):
        """Salva o objeto no banco de dados"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Remove o objeto do banco de dados"""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
