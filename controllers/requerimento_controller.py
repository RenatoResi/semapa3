from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from core.security import require_role
from services.requerimento_service import RequerimentoService
from services.requerente_service import RequerenteService
from services.arvore_service import ArvoreService
from services.ordem_servico_service import OrdemServicoService
from utils.validators import validate_required_fields
from utils.helpers import allowed_file, save_uploaded_file

requerimento_bp = Blueprint('requerimento', __name__, url_prefix='/requerimentos')

@requerimento_bp.route('/')
@login_required
@require_role(1)
def index():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

        status = request.args.get('status')
        tipo = request.args.get('tipo')
        requerente_id = request.args.get('requerente_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        search = request.args.get('search', '').strip()

        pagination = RequerimentoService.get_paginated(
            page=page,
            per_page=per_page,
            status=status,
            tipo=tipo,
            requerente_id=requerente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            search=search
        )

        requerimentos = pagination.items
        total = pagination.total
        total_pages = pagination.pages

        requerentes = RequerenteService.get_all(page=1, per_page=1000)[0]  # pegar todos para filtro
        tipos = RequerimentoService.get_tipos()
        status_list = RequerimentoService.get_status_list()

        return render_template('requerimentos/list.html',
                               requerimentos=requerimentos,
                               requerentes=requerentes,
                               tipos=tipos,
                               status_list=status_list,
                               page=page,
                               total_pages=total_pages,
                               total=total,
                               search=search,
                               status=status,
                               tipo=tipo,
                               requerente_id=requerente_id,
                               data_inicio=data_inicio,
                               data_fim=data_fim)

    except Exception as e:
        current_app.logger.error(f"Erro ao listar requerimentos: {str(e)}")
        flash('Erro ao carregar lista de requerimentos', 'error')
        return render_template('requerimentos/list.html', requerimentos=[], requerentes=[], tipos=[], status_list=[])

@requerimento_bp.route('/novo')
@login_required
@require_role(1)
def novo():
    try:
        requerentes = RequerenteService.get_all(page=1, per_page=1000)[0]
        arvores = ArvoreService.get_all()
        tipos = RequerimentoService.get_tipos()

        return render_template('requerimentos/form.html',
                               requerimento=None,
                               requerentes=requerentes,
                               arvores=arvores,
                               tipos=tipos)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('requerimento.index'))

@requerimento_bp.route('/criar', methods=['POST'])
@login_required
@require_role(1)
def criar():
    try:
        required_fields = ['requerente_id', 'arvore_id', 'tipo', 'justificativa']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('requerimento.novo'))

        data = {
            'requerente_id': int(request.form['requerente_id']),
            'arvore_id': int(request.form['arvore_id']),
            'tipo': request.form['tipo'],
            'justificativa': request.form['justificativa'].strip(),
            'observacoes': request.form.get('observacoes', '').strip(),
            'urgente': bool(request.form.get('urgente')),
            'created_by': current_user.id
        }

        documentos = request.files.getlist('documentos')
        data['documentos'] = []
        for doc in documentos:
            if doc and doc.filename and allowed_file(doc.filename):
                doc_path = save_uploaded_file(doc, 'requerimentos')
                data['documentos'].append(doc_path)

        requerimento = RequerimentoService.create(data)

        flash('Requerimento criado com sucesso!', 'success')
        return redirect(url_for('requerimento.detalhes', id=requerimento.id))

    except Exception as e:
        current_app.logger.error(f"Erro ao criar requerimento: {str(e)}")
        flash('Erro ao criar requerimento', 'error')
        return redirect(url_for('requerimento.novo'))

@requerimento_bp.route('/<int:id>')
@login_required
@require_role(1)
def detalhes(id):
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        historico = RequerimentoService.get_history(id)
        ordem_servico = OrdemServicoService.get_by_requerimento(id)

        return render_template('requerimentos/detalhes.html',
                               requerimento=requerimento,
                               historico=historico,
                               ordem_servico=ordem_servico)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar requerimento {id}: {str(e)}")
        flash('Erro ao carregar detalhes do requerimento', 'error')
        return redirect(url_for('requerimento.index'))

@requerimento_bp.route('/<int:id>/editar')
@login_required
@require_role(2)
def editar(id):
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        if not RequerimentoService.can_edit(id):
            flash('Requerimento não pode ser editado no status atual', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        requerentes = RequerenteService.get_all(page=1, per_page=1000)[0]
        arvores = ArvoreService.get_all()
        tipos = RequerimentoService.get_tipos()

        return render_template('requerimentos/form.html',
                               requerimento=requerimento,
                               requerentes=requerentes,
                               arvores=arvores,
                               tipos=tipos)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de edição: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('requerimento.index'))

@requerimento_bp.route('/<int:id>/atualizar', methods=['POST'])
@login_required
@require_role(2)
def atualizar(id):
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        if not RequerimentoService.can_edit(id):
            flash('Requerimento não pode ser editado no status atual', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        required_fields = ['requerente_id', 'arvore_id', 'tipo', 'justificativa']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('requerimento.editar', id=id))

        data = {
            'requerente_id': int(request.form['requerente_id']),
            'arvore_id': int(request.form['arvore_id']),
            'tipo': request.form['tipo'],
            'motivo': request.form['justificativa'].strip(),
            'observacao': request.form.get('observacoes', '').strip(),
            'urgente': bool(request.form.get('urgente')),
            'updated_by': current_user.id
        }

        documentos = request.files.getlist('documentos')
        novos_documentos = []
        for doc in documentos:
            if doc and doc.filename and allowed_file(doc.filename):
                doc_path = save_uploaded_file(doc, 'requerimentos')
                novos_documentos.append(doc_path)

        if novos_documentos:
            data['novos_documentos'] = novos_documentos

        RequerimentoService.update(id, data)

        flash('Requerimento atualizado com sucesso!', 'success')
        return redirect(url_for('requerimento.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar requerimento {id}: {str(e)}")
        flash('Erro ao atualizar requerimento', 'error')
        return redirect(url_for('requerimento.editar', id=id))

@requerimento_bp.route('/api/buscar')
@login_required
@require_role(1)
def buscar_api():
    term = request.args.get('term', '').strip()
    results = RequerimentoService.search(term)
    # Retorne uma lista de dicts com os campos necessários
    return jsonify([
        {
            'label': r.numero,
            'tipo': r.tipo,
            'status': r.status,
            'prioridade': r.prioridade,
            'data_abertura': r.data_abertura.strftime('%d/%m/%Y')
        } for r in results
    ])