# -*- coding: utf-8 -*-
"""
SEMAPA3 - Vistoria Model
Modelo para gerenciamento de vistorias técnicas
"""

from core.database import db, BaseModel
from datetime import datetime
import os

class Vistoria(BaseModel):
    """Modelo de vistoria técnica"""
    __tablename__ = 'vistorias'

    numero = db.Column(db.String(20), unique=True, nullable=False, index=True)
    arvore_id = db.Column(db.Integer, db.ForeignKey('arvores.id'), nullable=False)
    ordem_servico_id = db.Column(db.Integer, db.ForeignKey('ordens_servico.id'))
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_vistoria = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    laudo = db.Column(db.Text, nullable=False)
    recomendacoes = db.Column(db.Text)
    fotos = db.Column(db.Text)  # JSON com paths das fotos
    status = db.Column(db.String(20), default='realizada')

    def __init__(self, numero, arvore_id, tecnico_id, laudo, recomendacoes=None, 
                 ordem_servico_id=None, fotos=None):
        self.numero = numero
        self.arvore_id = arvore_id
        self.tecnico_id = tecnico_id
        self.laudo = laudo
        self.recomendacoes = recomendacoes
        self.ordem_servico_id = ordem_servico_id
        self.fotos = fotos

    @classmethod
    def generate_numero(cls):
        """Gera número sequencial para vistoria"""
        last_vistoria = cls.query.order_by(cls.id.desc()).first()
        if last_vistoria:
            last_num = int(last_vistoria.numero.split('/')[-1])
            return f"VT/{datetime.now().year}/{last_num + 1:04d}"
        return f"VT/{datetime.now().year}/0001"

    @classmethod
    def get_by_tecnico(cls, tecnico_id):
        """Retorna vistorias por técnico"""
        return cls.query.filter_by(tecnico_id=tecnico_id).order_by(cls.data_vistoria.desc()).all()

    @classmethod
    def get_by_periodo(cls, data_inicio, data_fim):
        """Retorna vistorias por período"""
        return cls.query.filter(
            cls.data_vistoria >= data_inicio,
            cls.data_vistoria <= data_fim
        ).order_by(cls.data_vistoria.desc()).all()

    def add_foto(self, foto_path):
        """Adiciona foto à vistoria"""
        import json
        fotos_list = json.loads(self.fotos) if self.fotos else []
        fotos_list.append(foto_path)
        self.fotos = json.dumps(fotos_list)
        self.save()

    def get_fotos(self):
        """Retorna lista de fotos"""
        import json
        return json.loads(self.fotos) if self.fotos else []

    def remove_foto(self, foto_path):
        """Remove foto da vistoria"""
        import json
        fotos_list = json.loads(self.fotos) if self.fotos else []
        if foto_path in fotos_list:
            fotos_list.remove(foto_path)
            # Remove arquivo físico
            try:
                if os.path.exists(foto_path):
                    os.remove(foto_path)
            except Exception:
                pass
            self.fotos = json.dumps(fotos_list)
            self.save()

    def __repr__(self):
        return f'<Vistoria {self.numero}>'
