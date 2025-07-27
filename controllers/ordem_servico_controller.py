from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date
from core.security import require_role
from services.ordem_servico_service import OrdemServicoService
from services.requerimento_service import RequerimentoService
from services.user_service import UserService
from utils.validators import validate_required_fields, validate_date

ordem_servico_bp = Blueprint('ordem_servico', __name__, url_prefix='/ordens-servico')

@ordem_servico_bp.route('/')
@login_required
@require_role(1)
def index():
    """Lista todas as ordens de serviço"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

        # Filtros
        status = request.args.get('status')
        prioridade = request.args.get('prioridade')
        responsavel_id = request.args.get('responsavel_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        search = request.args.get('search', '').strip()

        # Buscar ordens de serviço
        ordens = OrdemServicoService.get_paginated(
            page=page,
            per_page=per_page,
            status=status,
            prioridade=prioridade,
            responsavel_id=responsavel_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            search=search
        )

        # Dados para filtros
        responsaveis = UserService.get_technicians()
        status_list = OrdemServicoService.get_status_list()
        prioridades = OrdemServicoService.get_prioridades()

        return render_template('ordens_servico/index.html',
                             ordens=ordens,
                             responsaveis=responsaveis,
                             status_list=status_list,
                             prioridades=prioridades)

    except Exception as e:
        current_app.logger.error(f"Erro ao listar ordens de serviço: {str(e)}")
        flash('Erro ao carregar lista de ordens de serviço', 'error')
        return render_template('ordens_servico/index.html', ordens=None)

@ordem_servico_bp.route('/nova')
@login_required
@require_role(2)
def nova():
    """Formulário para nova ordem de serviço"""
    try:
        # Buscar requerimentos aprovados sem ordem de serviço
        requerimentos = RequerimentoService.get_approved_without_order()
        responsaveis = UserService.get_technicians()
        prioridades = OrdemServicoService.get_prioridades()

        return render_template('ordens_servico/form.html',
                             ordem=None,
                             requerimentos=requerimentos,
                             responsaveis=responsaveis,
                             prioridades=prioridades)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('ordem_servico.index'))

@ordem_servico_bp.route('/criar', methods=['POST'])
@login_required
@require_role(2)
def criar():
    """Cria nova ordem de serviço"""
    try:
        # Validar campos obrigatórios
        required_fields = ['requerimento_id', 'prioridade']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('ordem_servico.nova'))

        # Verificar se requerimento já possui ordem de serviço
        requerimento_id = int(request.form['requerimento_id'])
        if OrdemServicoService.exists_for_requerimento(requerimento_id):
            flash('Já existe ordem de serviço para este requerimento', 'error')
            return redirect(url_for('ordem_servico.nova'))

        # Dados da ordem de serviço
        data = {
            'requerimento_id': requerimento_id,
            'responsavel_id': int(request.form['responsavel_id']) if request.form.get('responsavel_id') else None,
            'prioridade': request.form['prioridade'],
            'data_prevista': datetime.strptime(request.form['data_prevista'], '%Y-%m-%d').date() if request.form.get('data_prevista') else None,
            'observacoes': request.form.get('observacoes', '').strip(),
            'status': 'pendente',
            'created_by': current_user.id
        }

        # Criar ordem de serviço
        ordem = OrdemServicoService.create(data)

        flash('Ordem de serviço criada com sucesso!', 'success')
        return redirect(url_for('ordem_servico.detalhes', id=ordem.id))

    except ValueError as e:
        flash(f'Data inválida: {str(e)}', 'error')
        return redirect(url_for('ordem_servico.nova'))
    except Exception as e:
        current_app.logger.error(f"Erro ao criar ordem de serviço: {str(e)}")
        flash('Erro ao criar ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.nova'))

@ordem_servico_bp.route('/<int:id>')
@login_required
@require_role(1)
def detalhes(id):
    """Exibe detalhes de uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        # Histórico de alterações
        historico = OrdemServicoService.get_history(id)

        # Vistorias relacionadas
        vistorias = OrdemServicoService.get_vistorias(id)

        return render_template('ordens_servico/detalhes.html',
                             ordem=ordem,
                             historico=historico,
                             vistorias=vistorias)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar ordem de serviço {id}: {str(e)}")
        flash('Erro ao carregar detalhes da ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.index'))

@ordem_servico_bp.route('/<int:id>/editar')
@login_required
@require_role(2)
def editar(id):
    """Formulário para editar ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        # Verificar se pode ser editada
        if not OrdemServicoService.can_edit(id):
            flash('Ordem de serviço não pode ser editada no status atual', 'error')
            return redirect(url_for('ordem_servico.detalhes', id=id))

        responsaveis = UserService.get_technicians()
        prioridades = OrdemServicoService.get_prioridades()

        return render_template('ordens_servico/form.html',
                             ordem=ordem,
                             requerimentos=None,  # Não permitir alterar requerimento
                             responsaveis=responsaveis,
                             prioridades=prioridades)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de edição: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('ordem_servico.index'))

@ordem_servico_bp.route('/<int:id>/atualizar', methods=['POST'])
@login_required
@require_role(2)
def atualizar(id):
    """Atualiza uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        # Verificar se pode ser editada
        if not OrdemServicoService.can_edit(id):
            flash('Ordem de serviço não pode ser editada no status atual', 'error')
            return redirect(url_for('ordem_servico.detalhes', id=id))

        # Dados para atualização
        data = {
            'responsavel_id': int(request.form['responsavel_id']) if request.form.get('responsavel_id') else None,
            'prioridade': request.form['prioridade'],
            'data_prevista': datetime.strptime(request.form['data_prevista'], '%Y-%m-%d').date() if request.form.get('data_prevista') else None,
            'observacoes': request.form.get('observacoes', '').strip(),
            'updated_by': current_user.id
        }

        # Atualizar ordem de serviço
        OrdemServicoService.update(id, data)

        flash('Ordem de serviço atualizada com sucesso!', 'success')
        return redirect(url_for('ordem_servico.detalhes', id=id))

    except ValueError as e:
        flash(f'Data inválida: {str(e)}', 'error')
        return redirect(url_for('ordem_servico.editar', id=id))
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar ordem de serviço {id}: {str(e)}")
        flash('Erro ao atualizar ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.editar', id=id))

@ordem_servico_bp.route('/<int:id>/iniciar', methods=['POST'])
@login_required
@require_role(2)
def iniciar(id):
    """Inicia execução de uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        # Atribuir responsável se não tiver
        responsavel_id = request.form.get('responsavel_id', type=int)
        if not ordem.responsavel_id and responsavel_id:
            OrdemServicoService.assign_technician(id, responsavel_id, current_user.id)

        # Iniciar ordem de serviço
        OrdemServicoService.start(id, current_user.id)

        flash('Ordem de serviço iniciada!', 'success')
        return redirect(url_for('ordem_servico.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar ordem de serviço {id}: {str(e)}")
        flash('Erro ao iniciar ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.detalhes', id=id))

@ordem_servico_bp.route('/<int:id>/pausar', methods=['POST'])
@login_required
@require_role(2)
def pausar(id):
    """Pausa execução de uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        motivo = request.form.get('motivo', '').strip()

        # Pausar ordem de serviço
        OrdemServicoService.pause(id, motivo, current_user.id)

        flash('Ordem de serviço pausada!', 'warning')
        return redirect(url_for('ordem_servico.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao pausar ordem de serviço {id}: {str(e)}")
        flash('Erro ao pausar ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.detalhes', id=id))

@ordem_servico_bp.route('/<int:id>/concluir', methods=['POST'])
@login_required
@require_role(2)
def concluir(id):
    """Conclui uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        relatorio = request.form.get('relatorio', '').strip()
        if not relatorio:
            flash('Relatório de conclusão é obrigatório', 'error')
            return redirect(url_for('ordem_servico.detalhes', id=id))

        # Concluir ordem de serviço
        OrdemServicoService.complete(id, relatorio, current_user.id)

        flash('Ordem de serviço concluída com sucesso!', 'success')
        return redirect(url_for('ordem_servico.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao concluir ordem de serviço {id}: {str(e)}")
        flash('Erro ao concluir ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.detalhes', id=id))

@ordem_servico_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
@require_role(3)
def cancelar(id):
    """Cancela uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        motivo = request.form.get('motivo', '').strip()
        if not motivo:
            flash('Motivo do cancelamento é obrigatório', 'error')
            return redirect(url_for('ordem_servico.detalhes', id=id))

        # Cancelar ordem de serviço
        OrdemServicoService.cancel(id, motivo, current_user.id)

        flash('Ordem de serviço cancelada!', 'warning')
        return redirect(url_for('ordem_servico.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao cancelar ordem de serviço {id}: {str(e)}")
        flash('Erro ao cancelar ordem de serviço', 'error')
        return redirect(url_for('ordem_servico.detalhes', id=id))

@ordem_servico_bp.route('/<int:id>/atribuir', methods=['POST'])
@login_required
@require_role(2)
def atribuir(id):
    """Atribui técnico a uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            flash('Ordem de serviço não encontrada', 'error')
            return redirect(url_for('ordem_servico.index'))

        responsavel_id = request.form.get('responsavel_id', type=int)
        if not responsavel_id:
            flash('Selecione um técnico responsável', 'error')
            return redirect(url_for('ordem_servico.detalhes', id=id))

        # Atribuir técnico
        OrdemServicoService.assign_technician(id, responsavel_id, current_user.id)

        flash('Técnico atribuído com sucesso!', 'success')
        return redirect(url_for('ordem_servico.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao atribuir técnico: {str(e)}")
        flash('Erro ao atribuir técnico', 'error')
        return redirect(url_for('ordem_servico.detalhes', id=id))

@ordem_servico_bp.route('/agenda')
@login_required
@require_role(1)
def agenda():
    """Agenda de ordens de serviço"""
    try:
        # Ordens agendadas para hoje
        hoje = date.today()
        ordens_hoje = OrdemServicoService.get_by_date(hoje)

        # Ordens em atraso
        ordens_atrasadas = OrdemServicoService.get_overdue()

        # Próximas ordens (7 dias)
        proximas_ordens = OrdemServicoService.get_upcoming(7)

        return render_template('ordens_servico/agenda.html',
                             ordens_hoje=ordens_hoje,
                             ordens_atrasadas=ordens_atrasadas,
                             proximas_ordens=proximas_ordens)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar agenda: {str(e)}")
        flash('Erro ao carregar agenda', 'error')
        return redirect(url_for('ordem_servico.index'))

@ordem_servico_bp.route('/relatorio')
@login_required
@require_role(2)
def relatorio():
    """Relatório de ordens de serviço"""
    try:
        # Parâmetros do relatório
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        status = request.args.get('status')
        responsavel_id = request.args.get('responsavel_id', type=int)

        # Gerar relatório
        dados = OrdemServicoService.generate_report(
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            responsavel_id=responsavel_id
        )

        # Dados para filtros
        responsaveis = UserService.get_technicians()

        return render_template('ordens_servico/relatorio.html',
                             dados=dados,
                             responsaveis=responsaveis)

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório: {str(e)}")
        flash('Erro ao gerar relatório', 'error')
        return redirect(url_for('ordem_servico.index'))

@ordem_servico_bp.route('/api/status/<int:id>')
@login_required
def api_status(id):
    """API para obter status de uma ordem de serviço"""
    try:
        ordem = OrdemServicoService.get_by_id(id)
        if not ordem:
            return jsonify({'error': 'Ordem não encontrada'}), 404

        return jsonify({
            'id': ordem.id,
            'status': ordem.status,
            'progresso': ordem.progresso,
            'data_inicio': ordem.data_inicio.isoformat() if ordem.data_inicio else None,
            'data_conclusao': ordem.data_conclusao.isoformat() if ordem.data_conclusao else None
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter status: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500