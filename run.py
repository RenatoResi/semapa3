#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEMAPA3 - Sistema de Gestão Municipal de Árvores e Podas
Arquivo principal de execução da aplicação
"""

import sys
import os

# Adicionar o diretório raiz ao path para facilitar imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import config

# Definir dinamicamente o ambiente/configuração a ser usada
config_name = os.environ.get('FLASK_CONFIG', 'default')
app_config = config.get(config_name)

try:
    app = create_app(app_config)
    print("✅ Aplicação SEMAPA3 iniciada com sucesso!")
    print("🌐 Acesse: http://localhost:5000")
except Exception as e:
    print(f"❌ Erro ao iniciar aplicação: {e}")
    sys.exit(1)

if __name__ == '__main__':
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )
