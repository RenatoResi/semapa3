# -*- coding: utf-8 -*-
"""
SEMAPA3 - VistoriaFoto Model
Modelo para fotos de vistoria conforme DDL da tabela vistoria_foto
"""

from core.database import db, BaseModel


class VistoriaFoto(BaseModel):
    """Modelo de foto de vistoria"""
    __tablename__ = 'vistoria_foto'

    id = db.Column(db.Integer, primary_key=True)
    vistoria_id = db.Column(db.Integer, db.ForeignKey('vistoria.id', ondelete='CASCADE'), nullable=False)
    arquivo_nome = db.Column(db.String(255), nullable=True)
    arquivo = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, vistoria_id, arquivo, arquivo_nome=None):
        self.vistoria_id = vistoria_id
        self.arquivo = arquivo
        self.arquivo_nome = arquivo_nome

    @classmethod
    def get_by_vistoria(cls, vistoria_id):
        """Retorna fotos por vistoria"""
        return cls.query.filter_by(vistoria_id=vistoria_id).all()

    @property
    def tamanho_arquivo(self):
        """Retorna tamanho do arquivo em bytes"""
        return len(self.arquivo) if self.arquivo else 0

    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data['tamanho_arquivo'] = self.tamanho_arquivo
        # Remove o campo arquivo binário do dicionário por ser muito grande
        data.pop('arquivo', None)
        return data

    def __repr__(self):
        return f'<VistoriaFoto {self.id} - {self.arquivo_nome}>'
