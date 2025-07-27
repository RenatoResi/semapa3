from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, send_file
from flask_login import login_required, current_user
from datetime import datetime
from core.security import require_role
from services.requerimento_service import RequerimentoService
from services.arvore_service import ArvoreService
from services.requerente_service import RequerenteService
from services.ordem_servico_service import OrdemServicoService
from utils.validators import validate_required_fields
from utils.helpers import allowed_file, save_uploaded_file
import io

requerimento_bp = Blueprint('requerimento', __name__, url_prefix='/requerimentos')

@requerimento_bp.route('/')
@login_required
@require_role(1)
def index():
    """Lista todos os requerimentos"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

        # Filtros
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        requerente_id = request.args.get('requerente_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        search = request.args.get('search', '').strip()

        # Buscar requerimentos
        requerimentos = RequerimentoService.get_paginated(
            page=page,
            per_page=per_page,
            status=status,
            tipo=tipo,
            requerente_id=requerente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            search=search
        )

        # Dados para filtros
        requerentes = RequerenteService.get_all()
        tipos = RequerimentoService.get_tipos()
        status_list = RequerimentoService.get_status_list()

        return render_template('requerimentos/index.html',
                             requerimentos=requerimentos,
                             requerentes=requerentes,
                             tipos=tipos,
                             status_list=status_list)

    except Exception as e:
        current_app.logger.error(f"Erro ao listar requerimentos: {str(e)}")
        flash('Erro ao carregar lista de requerimentos', 'error')
        return render_template('requerimentos/index.html', requerimentos=None)

@requerimento_bp.route('/novo')
@login_required
@require_role(1)
def novo():
    """Formulário para novo requerimento"""
    try:
        requerentes = RequerenteService.get_all()
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
    """Cria novo requerimento"""
    try:
        # Validar campos obrigatórios
        required_fields = ['requerente_id', 'arvore_id', 'tipo', 'justificativa']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('requerimento.novo'))

        # Dados do requerimento
        data = {
            'requerente_id': int(request.form['requerente_id']),
            'arvore_id': int(request.form['arvore_id']),
            'tipo': request.form['tipo'],
            'justificativa': request.form['justificativa'].strip(),
            'observacoes': request.form.get('observacoes', '').strip(),
            'urgente': bool(request.form.get('urgente')),
            'status': 'pendente',
            'created_by': current_user.id
        }

        # Processar uploads de documentos
        documentos = request.files.getlist('documentos')
        data['documentos'] = []
        for doc in documentos:
            if doc and doc.filename and allowed_file(doc.filename):
                doc_path = save_uploaded_file(doc, 'requerimentos')
                data['documentos'].append(doc_path)

        # Criar requerimento
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
    """Exibe detalhes de um requerimento"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        # Histórico de alterações
        historico = RequerimentoService.get_history(id)

        # Ordem de serviço relacionada
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
    """Formulário para editar requerimento"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        # Verificar se pode ser editado
        if not RequerimentoService.can_edit(id):
            flash('Requerimento não pode ser editado no status atual', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        requerentes = RequerenteService.get_all()
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
    """Atualiza um requerimento"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        # Verificar se pode ser editado
        if not RequerimentoService.can_edit(id):
            flash('Requerimento não pode ser editado no status atual', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        # Validar campos obrigatórios
        required_fields = ['requerente_id', 'arvore_id', 'tipo', 'justificativa']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('requerimento.editar', id=id))

        # Dados para atualização
        data = {
            'requerente_id': int(request.form['requerente_id']),
            'arvore_id': int(request.form['arvore_id']),
            'tipo': request.form['tipo'],
            'justificativa': request.form['justificativa'].strip(),
            'observacoes': request.form.get('observacoes', '').strip(),
            'urgente': bool(request.form.get('urgente')),
            'updated_by': current_user.id
        }

        # Processar novos documentos
        documentos = request.files.getlist('documentos')
        novos_documentos = []
        for doc in documentos:
            if doc and doc.filename and allowed_file(doc.filename):
                doc_path = save_uploaded_file(doc, 'requerimentos')
                novos_documentos.append(doc_path)

        if novos_documentos:
            data['novos_documentos'] = novos_documentos

        # Atualizar requerimento
        RequerimentoService.update(id, data)

        flash('Requerimento atualizado com sucesso!', 'success')
        return redirect(url_for('requerimento.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar requerimento {id}: {str(e)}")
        flash('Erro ao atualizar requerimento', 'error')
        return redirect(url_for('requerimento.editar', id=id))

@requerimento_bp.route('/<int:id>/aprovar', methods=['POST'])
@login_required
@require_role(2)
def aprovar(id):
    """Aprova um requerimento"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        parecer = request.form.get('parecer', '').strip()

        # Aprovar requerimento
        RequerimentoService.approve(id, parecer, current_user.id)

        flash('Requerimento aprovado com sucesso!', 'success')
        return redirect(url_for('requerimento.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao aprovar requerimento {id}: {str(e)}")
        flash('Erro ao aprovar requerimento', 'error')
        return redirect(url_for('requerimento.detalhes', id=id))

@requerimento_bp.route('/<int:id>/rejeitar', methods=['POST'])
@login_required
@require_role(2)
def rejeitar(id):
    """Rejeita um requerimento"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrada', 'error')
            return redirect(url_for('requerimento.index'))

        motivo = request.form.get('motivo', '').strip()
        if not motivo:
            flash('Motivo da rejeição é obrigatório', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        # Rejeitar requerimento
        RequerimentoService.reject(id, motivo, current_user.id)

        flash('Requerimento rejeitado!', 'warning')
        return redirect(url_for('requerimento.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao rejeitar requerimento {id}: {str(e)}")
        flash('Erro ao rejeitar requerimento', 'error')
        return redirect(url_for('requerimento.detalhes', id=id))

@requerimento_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
@require_role(2)
def cancelar(id):
    """Cancela um requerimento"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        motivo = request.form.get('motivo', '').strip()

        # Cancelar requerimento 
        RequerimentoService.cancel(id, motivo, current_user.id)

        flash('Requerimento cancelado!', 'warning')
        return redirect(url_for('requerimento.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao cancelar requerimento {id}: {str(e)}")
        flash('Erro ao cancelar requerimento', 'error')
        return redirect(url_for('requerimento.detalhes', id=id))

@requerimento_bp.route('/<int:id>/gerar-ordem', methods=['POST'])
@login_required
@require_role(2)
def gerar_ordem(id):
    """Gera ordem de serviço para requerimento aprovado"""
    try:
        requerimento = RequerimentoService.get_by_id(id)
        if not requerimento:
            flash('Requerimento não encontrado', 'error')
            return redirect(url_for('requerimento.index'))

        if requerimento.status != 'aprovado':
            flash('Só é possível gerar ordem de serviço para requerimentos aprovados', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        # Verificar se já existe ordem de serviço
        if OrdemServicoService.exists_for_requerimento(id):
            flash('Já existe ordem de serviço para este requerimento', 'error')
            return redirect(url_for('requerimento.detalhes', id=id))

        # Dados da ordem de serviço
        data = {
            'requerimento_id': id,
            'prioridade': 'alta' if requerimento.urgente else 'normal',
            'observacoes': request.form.get('observacoes', '').strip(),
            'created_by': current_user.id
        }

        # Criar ordem de serviço
        ordem = OrdemServicoService.create(data)

        flash('Ordem de serviço gerada com sucesso!', 'success')
        return redirect(url_for('ordem_servico.detalhes', id=ordem.id))

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar ordem de serviço: {str(e)}")
        flash('Erro ao gerar ordem de serviço', 'error')
        return redirect(url_for('requerimento.detalhes', id=id))

@requerimento_bp.route('/relatorio')
@login_required
@require_role(2)
def relatorio():
    """Relatório de requerimentos"""
    try:
        # Parâmetros do relatório
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo = request.args.get('tipo')
        status = request.args.get('status')

        # Gerar relatório
        dados = RequerimentoService.generate_report(
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo=tipo,
            status=status
        )

        return render_template('requerimentos/relatorio.html', dados=dados)

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório: {str(e)}")
        flash('Erro ao gerar relatório', 'error')
        return redirect(url_for('requerimento.index'))

@requerimento_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar requerimentos (AJAX)"""
    try:
        term = request.args.get('term', '').strip()
        limit = request.args.get('limit', 10, type=int)

        if len(term) < 2:
            return jsonify([])

        requerimentos = RequerimentoService.search(term, limit)

        return jsonify([{
            'id': r.id,
            'label': f"Req. #{r.id} - {r.tipo.title()} - {r.requerente.nome}",
            'value': r.id,
            'tipo': r.tipo,
            'status': r.status
        } for r in requerimentos])

    except Exception as e:
        current_app.logger.error(f"Erro na busca de requerimentos: {str(e)}")
        return jsonify([])