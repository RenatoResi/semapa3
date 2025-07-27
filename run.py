#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEMAPA3 - Sistema de Gestão Municipal de Árvores e Podas
Arquivo principal de execução da aplicação
"""

from app import create_app
from config.settings import Config

app = create_app(Config)

if __name__ == '__main__':
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', False)
    )
