# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerente Controller
Controller de gerenciamento de requerentes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from services.requerente_service import RequerenteService
from core.exceptions import ValidationError, NotFoundError
from core.security import require_role

requerente_bp = Blueprint('requerente', __name__, url_prefix='/requerentes')

@requerente_bp.route('/')
@login_required
def index():
    """Lista de requerentes"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    try:
        if search:
            requerentes, total = RequerenteService.search(search, page=page)
        else:
            requerentes, total = RequerenteService.get_all(page=page)

        return render_template('requerentes/index.html',
                             requerentes=requerentes,
                             total=total,
                             search=search,
                             page=page)
    except Exception as e:
        flash(f'Erro ao carregar requerentes: {str(e)}', 'error')
        return render_template('requerentes/index.html', requerentes=[], total=0)

@requerente_bp.route('/new', methods=['GET', 'POST'])
@login_required
@require_role('tecnico')
def create():
    """Criar novo requerente"""
    if request.method == 'POST':
        try:
            requerente = RequerenteService.create(
                nome=request.form.get('nome'),
                cpf_cnpj=request.form.get('cpf_cnpj'),
                tipo=request.form.get('tipo'),
                telefone=request.form.get('telefone'),
                email=request.form.get('email'),
                endereco=request.form.get('endereco')
            )

            flash('Requerente cadastrado com sucesso!', 'success')
            return redirect(url_for('requerente.view', id=requerente.id))

        except ValidationError as e:
            flash(str(e), 'error')

    return render_template('requerentes/form.html')

@requerente_bp.route('/<int:id>')
@login_required
def view(id):
    """Visualizar requerente"""
    try:
        requerente = RequerenteService.get_by_id(id)
        return render_template('requerentes/view.html', requerente=requerente)
    except NotFoundError as e:
        flash(str(e), 'error')
        return redirect(url_for('requerente.index'))

@requerente_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('tecnico')
def edit(id):
    """Editar requerente"""
    try:
        requerente = RequerenteService.get_by_id(id)

        if request.method == 'POST':
            RequerenteService.update(id, **{
                'nome': request.form.get('nome'),
                'telefone': request.form.get('telefone'),
                'email': request.form.get('email'),
                'endereco': request.form.get('endereco')
            })

            flash('Requerente atualizado com sucesso!', 'success')
            return redirect(url_for('requerente.view', id=id))

        return render_template('requerentes/form.html', requerente=requerente, editing=True)

    except (NotFoundError, ValidationError) as e:
        flash(str(e), 'error')
        return redirect(url_for('requerente.index'))

@requerente_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@require_role('admin')
def delete(id):
    """Excluir requerente"""
    try:
        RequerenteService.delete(id)
        flash('Requerente excluído com sucesso!', 'success')
    except (NotFoundError, ValidationError) as e:
        flash(str(e), 'error')

    return redirect(url_for('requerente.index'))

@requerente_bp.route('/api/search')
@login_required
def api_search():
    """API de busca de requerentes"""
    query = request.args.get('q', '')
    try:
        requerentes, _ = RequerenteService.search(query, per_page=10)
        return jsonify([{
            'id': r.id,
            'nome': r.nome,
            'cpf_cnpj': r.cpf_cnpj,
            'tipo': r.tipo
        } for r in requerentes])
    except Exception:
        return jsonify([])
