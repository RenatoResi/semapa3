# -*- coding: utf-8 -*-
"""
SEMAPA3 - Core Database
Configuração do banco de dados usando SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy

# Instância global do SQLAlchemy
db = SQLAlchemy()

class BaseModel(db.Model):
    """Modelo base abstrato com utilitários comuns, sem impor campos."""
    __abstract__ = True

    def save(self):
        """Salva o objeto no banco de dados."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Remove o objeto do banco de dados."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self, exclude_fields=None):
        """Converte o objeto para dicionário."""
        exclude_fields = exclude_fields or []
        data = {}
        for c in self.__table__.columns:
            if c.name not in exclude_fields:
                value = getattr(self, c.name)
                # Caso timestamp, converte para isoformat
                if hasattr(value, "isoformat"):
                    value = value.isoformat()
                data[c.name] = value
        return data

    @classmethod
    def get_or_404(cls, id):
        """Busca por ID ou lança 404."""
        from flask import abort
        obj = cls.query.get(id)
        if not obj:
            abort(404)
        return obj

    def __repr__(self):
        name = getattr(self, "id", None) or getattr(self, "numero", None) or "new"
        return f"<{self.__class__.__name__} {name}>"
