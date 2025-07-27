# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerente Controller
Controller para gestão de requerentes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from core.security import require_role
from services.requerente_service import RequerenteService
from utils.validators import validate_cpf, validate_cnpj, validate_email
from utils.helpers import format_document

# CORREÇÃO: Blueprint com nome 'requerente' (singular)
requerente_bp = Blueprint('requerente', __name__, url_prefix='/requerentes')

@requerente_bp.route('/')
@login_required
@require_role(1)
def index():
    """Lista todos os requerentes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
        
        # Filtros
        tipo = request.args.get('tipo')
        search = request.args.get('search', '').strip()
        
        requerentes = RequerenteService.get_paginated(
            page=page,
            per_page=per_page,
            tipo=tipo,
            search=search
        )
        
        return render_template('requerentes/index.html', requerentes=requerentes)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar requerentes: {str(e)}")
        flash('Erro ao carregar lista de requerentes', 'error')
        return render_template('requerentes/index.html', requerentes=None)

@requerente_bp.route('/novo')
@login_required
@require_role(2)
def novo():
    """Formulário para novo requerente"""
    return render_template('requerentes/form.html', requerente=None)

@requerente_bp.route('/criar', methods=['POST'])
@login_required
@require_role(2)
def criar():
    """Cria novo requerente"""
    try:
        data = {
            'nome': request.form.get('nome', '').strip(),
            'tipo': request.form.get('tipo'),
            'documento': request.form.get('documento', '').strip(),
            'email': request.form.get('email', '').strip(),
            'telefone': request.form.get('telefone', '').strip(),
            'endereco': request.form.get('endereco', '').strip(),
            'created_by': current_user.id
        }
        
        # Validações
        if not data['nome']:
            flash('Nome é obrigatório', 'error')
            return render_template('requerentes/form.html', requerente=None)
            
        if data['tipo'] == 'PF' and not validate_cpf(data['documento']):
            flash('CPF inválido', 'error')
            return render_template('requerentes/form.html', requerente=None)
            
        if data['tipo'] == 'PJ' and not validate_cnpj(data['documento']):
            flash('CNPJ inválido', 'error')
            return render_template('requerentes/form.html', requerente=None)
        
        # Criar requerente
        requerente = RequerenteService.create(data)
        
        flash('Requerente cadastrado com sucesso!', 'success')
        return redirect(url_for('requerente.detalhes', id=requerente.id))
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar requerente: {str(e)}")
        flash('Erro ao cadastrar requerente', 'error')
        return render_template('requerentes/form.html', requerente=None)

@requerente_bp.route('/<int:id>')
@login_required
@require_role(1)
def detalhes(id):
    """Exibe detalhes de um requerente"""
    try:
        requerente = RequerenteService.get_by_id(id)
        if not requerente:
            flash('Requerente não encontrado', 'error')
            return redirect(url_for('requerente.index'))
            
        return render_template('requerentes/detalhes.html', requerente=requerente)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar requerente {id}: {str(e)}")
        flash('Erro ao carregar requerente', 'error')
        return redirect(url_for('requerente.index'))

# Adicionar outras rotas necessárias...