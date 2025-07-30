# -*- coding: utf-8 -*-
"""
SEMAPA3 - Models Package
Centraliza importação de todos os modelos ajustados conforme DDLs
"""

from .user_model import User
from .especie_model import Especie
from .requerente_model import Requerente
from .arvore_model import Arvore
from .requerimento_model import Requerimento
from .ordem_servico_model import OrdemServico
from .vistoria_model import Vistoria
from .vistoria_foto_model import VistoriaFoto
from .associations import ordem_servico_requerimento

__all__ = [
    'User',
    'Especie',
    'Requerente', 
    'Arvore',
    'Requerimento',
    'OrdemServico',
    'Vistoria',
    'VistoriaFoto',
    'ordem_servico_requerimento'
]
