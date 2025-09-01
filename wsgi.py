# -*- coding: utf-8 -*-
"""
Ponto de entrada WSGI para a aplicação.
Usado pelo comando 'flask' e por servidores de produção como Gunicorn.
"""
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')