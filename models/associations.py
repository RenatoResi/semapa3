# -*- coding: utf-8 -*-
"""
SEMAPA3 - Tabela de Associação
Tabela many-to-many entre OrdemServico e Requerimento
"""

from core.database import db

# Tabela de associação many-to-many
ordem_servico_requerimento = db.Table(
    'ordem_servico_requerimento',
    db.Column('ordem_servico_id', db.Integer, db.ForeignKey('ordens_servico.id'), primary_key=True),
    db.Column('requerimento_id', db.Integer, db.ForeignKey('requerimentos.id'), primary_key=True)
)
