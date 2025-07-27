from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from core.security import require_role
from services.vistoria_service import VistoriaService
from services.ordem_servico_service import OrdemServicoService
from services.arvore_service import ArvoreService
from services.user_service import UserService
from utils.validators import validate_required_fields
from utils.helpers import allowed_file, save_uploaded_file

vistoria_bp = Blueprint('vistoria', __name__, url_prefix='/vistorias')

@vistoria_bp.route('/')
@login_required
@require_role(1)
def index():
    """Lista todas as vistorias"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

        # Filtros
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        tecnico_id = request.args.get('tecnico_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        search = request.args.get('search', '').strip()

        # Buscar vistorias
        vistorias = VistoriaService.get_paginated(
            page=page,
            per_page=per_page,
            status=status,
            tipo=tipo,
            tecnico_id=tecnico_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            search=search
        )

        # Dados para filtros
        tecnicos = UserService.get_technicians()
        tipos = VistoriaService.get_tipos()
        status_list = VistoriaService.get_status_list()

        return render_template('vistorias/index.html',
                             vistorias=vistorias,
                             tecnicos=tecnicos,
                             tipos=tipos,
                             status_list=status_list)

    except Exception as e:
        current_app.logger.error(f"Erro ao listar vistorias: {str(e)}")
        flash('Erro ao carregar lista de vistorias', 'error')
        return render_template('vistorias/index.html', vistorias=None)

@vistoria_bp.route('/nova')
@login_required
@require_role(2)
def nova():
    """Formulário para nova vistoria"""
    try:
        # Tipo de vistoria (ordem de serviço ou avulsa)
        tipo = request.args.get('tipo', 'avulsa')

        # Se for para ordem de serviço, buscar ordens em execução
        ordens_servico = []
        if tipo == 'ordem_servico':
            ordem_id = request.args.get('ordem_id', type=int)
            if ordem_id:
                ordem = OrdemServicoService.get_by_id(ordem_id)
                if ordem:
                    ordens_servico = [ordem]
            else:
                ordens_servico = OrdemServicoService.get_in_progress()

        # Buscar árvores e técnicos
        arvores = ArvoreService.get_all()
        tecnicos = UserService.get_technicians()
        tipos_vistoria = VistoriaService.get_tipos()

        return render_template('vistorias/form.html',
                             vistoria=None,
                             tipo=tipo,
                             ordens_servico=ordens_servico,
                             arvores=arvores,
                             tecnicos=tecnicos,
                             tipos_vistoria=tipos_vistoria)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('vistoria.index'))

@vistoria_bp.route('/criar', methods=['POST'])
@login_required
@require_role(2)
def criar():
    """Cria nova vistoria"""
    try:
        # Validar campos obrigatórios
        required_fields = ['arvore_id', 'tipo', 'data_vistoria']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('vistoria.nova'))

        # Dados da vistoria
        data = {
            'arvore_id': int(request.form['arvore_id']),
            'ordem_servico_id': int(request.form['ordem_servico_id']) if request.form.get('ordem_servico_id') else None,
            'tipo': request.form['tipo'],
            'data_vistoria': datetime.strptime(request.form['data_vistoria'], '%Y-%m-%d').date(),
            'tecnico_id': int(request.form['tecnico_id']) if request.form.get('tecnico_id') else current_user.id,
            'observacoes_iniciais': request.form.get('observacoes_iniciais', '').strip(),
            'status': 'agendada',
            'created_by': current_user.id
        }

        # Criar vistoria
        vistoria = VistoriaService.create(data)

        flash('Vistoria criada com sucesso!', 'success')
        return redirect(url_for('vistoria.detalhes', id=vistoria.id))

    except ValueError as e:
        flash(f'Data inválida: {str(e)}', 'error')
        return redirect(url_for('vistoria.nova'))
    except Exception as e:
        current_app.logger.error(f"Erro ao criar vistoria: {str(e)}")
        flash('Erro ao criar vistoria', 'error')
        return redirect(url_for('vistoria.nova'))

@vistoria_bp.route('/<int:id>')
@login_required
@require_role(1)
def detalhes(id):
    """Exibe detalhes de uma vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        return render_template('vistorias/detalhes.html', vistoria=vistoria)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar vistoria {id}: {str(e)}")
        flash('Erro ao carregar detalhes da vistoria', 'error')
        return redirect(url_for('vistoria.index'))

@vistoria_bp.route('/<int:id>/editar')
@login_required
@require_role(2)
def editar(id):
    """Formulário para editar vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        # Verificar se pode ser editada
        if not VistoriaService.can_edit(id):
            flash('Vistoria não pode ser editada no status atual', 'error')
            return redirect(url_for('vistoria.detalhes', id=id))

        # Dados para o formulário
        arvores = ArvoreService.get_all()
        tecnicos = UserService.get_technicians()
        tipos_vistoria = VistoriaService.get_tipos()

        return render_template('vistorias/form.html',
                             vistoria=vistoria,
                             tipo='editar',
                             ordens_servico=[],
                             arvores=arvores,
                             tecnicos=tecnicos,
                             tipos_vistoria=tipos_vistoria)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de edição: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('vistoria.index'))

@vistoria_bp.route('/<int:id>/realizar')
@login_required
@require_role(2)
def realizar(id):
    """Formulário para realizar vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        # Verificar se pode ser realizada
        if vistoria.status not in ['agendada', 'em_andamento']:
            flash('Vistoria não pode ser realizada no status atual', 'error')
            return redirect(url_for('vistoria.detalhes', id=id))

        return render_template('vistorias/realizar.html', vistoria=vistoria)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de vistoria: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('vistoria.detalhes', id=id))

@vistoria_bp.route('/<int:id>/executar', methods=['POST'])
@login_required
@require_role(2)
def executar(id):
    """Executa/finaliza uma vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        # Verificar se pode ser executada
        if vistoria.status not in ['agendada', 'em_andamento']:
            flash('Vistoria não pode ser executada no status atual', 'error')
            return redirect(url_for('vistoria.detalhes', id=id))

        # Dados da execução
        data = {
            'data_execucao': datetime.now(),
            'condicao_arvore': request.form.get('condicao_arvore'),
            'altura_atual': float(request.form['altura_atual']) if request.form.get('altura_atual') else None,
            'dap_atual': float(request.form['dap_atual']) if request.form.get('dap_atual') else None,
            'condicao_raiz': request.form.get('condicao_raiz'),
            'condicao_tronco': request.form.get('condicao_tronco'),
            'condicao_copa': request.form.get('condicao_copa'),
            'pragas_doencas': request.form.get('pragas_doencas', '').strip(),
            'risco_queda': request.form.get('risco_queda'),
            'interferencias': request.form.get('interferencias', '').strip(),
            'recomendacoes': request.form.get('recomendacoes', '').strip(),
            'observacoes_finais': request.form.get('observacoes_finais', '').strip(),
            'parecer_tecnico': request.form.get('parecer_tecnico', '').strip(),
            'status': 'concluida',
            'updated_by': current_user.id
        }

        # Processar upload de fotos
        fotos = request.files.getlist('fotos')
        fotos_paths = []
        for foto in fotos:
            if foto and foto.filename and allowed_file(foto.filename):
                foto_path = save_uploaded_file(foto, 'vistorias')
                fotos_paths.append(foto_path)

        if fotos_paths:
            data['fotos'] = fotos_paths

        # Atualizar vistoria
        VistoriaService.execute(id, data)

        flash('Vistoria realizada com sucesso!', 'success')
        return redirect(url_for('vistoria.detalhes', id=id))

    except ValueError as e:
        flash(f'Dados inválidos: {str(e)}', 'error')
        return redirect(url_for('vistoria.realizar', id=id))
    except Exception as e:
        current_app.logger.error(f"Erro ao executar vistoria {id}: {str(e)}")
        flash('Erro ao executar vistoria', 'error')
        return redirect(url_for('vistoria.realizar', id=id))

@vistoria_bp.route('/<int:id>/iniciar', methods=['POST'])
@login_required
@require_role(2)
def iniciar(id):
    """Inicia uma vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        # Iniciar vistoria
        VistoriaService.start(id, current_user.id)

        flash('Vistoria iniciada!', 'success')
        return redirect(url_for('vistoria.realizar', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar vistoria {id}: {str(e)}")
        flash('Erro ao iniciar vistoria', 'error')
        return redirect(url_for('vistoria.detalhes', id=id))

@vistoria_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
@require_role(2)
def cancelar(id):
    """Cancela uma vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        motivo = request.form.get('motivo', '').strip()

        # Cancelar vistoria
        VistoriaService.cancel(id, motivo, current_user.id)

        flash('Vistoria cancelada!', 'warning')
        return redirect(url_for('vistoria.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao cancelar vistoria {id}: {str(e)}")
        flash('Erro ao cancelar vistoria', 'error')
        return redirect(url_for('vistoria.detalhes', id=id))

@vistoria_bp.route('/<int:id>/reagendar', methods=['POST'])
@login_required
@require_role(2)
def reagendar(id):
    """Reagenda uma vistoria"""
    try:
        vistoria = VistoriaService.get_by_id(id)
        if not vistoria:
            flash('Vistoria não encontrada', 'error')
            return redirect(url_for('vistoria.index'))

        nova_data = request.form.get('nova_data')
        motivo = request.form.get('motivo', '').strip()

        if not nova_data:
            flash('Nova data é obrigatória', 'error')
            return redirect(url_for('vistoria.detalhes', id=id))

        # Reagendar vistoria
        nova_data_obj = datetime.strptime(nova_data, '%Y-%m-%d').date()
        VistoriaService.reschedule(id, nova_data_obj, motivo, current_user.id)

        flash('Vistoria reagendada com sucesso!', 'success')
        return redirect(url_for('vistoria.detalhes', id=id))

    except ValueError as e:
        flash(f'Data inválida: {str(e)}', 'error')
        return redirect(url_for('vistoria.detalhes', id=id))
    except Exception as e:
        current_app.logger.error(f"Erro ao reagendar vistoria {id}: {str(e)}")
        flash('Erro ao reagendar vistoria', 'error')
        return redirect(url_for('vistoria.detalhes', id=id))

@vistoria_bp.route('/agenda')
@login_required
@require_role(1) 
def agenda():
    """Agenda de vistorias"""
    try:
        # Vistorias agendadas para hoje
        hoje = datetime.now().date()
        vistorias_hoje = VistoriaService.get_by_date(hoje)

        # Vistorias em atraso
        vistorias_atrasadas = VistoriaService.get_overdue()

        # Próximas vistorias (7 dias)
        proximas_vistorias = VistoriaService.get_upcoming(7)

        # Vistorias por técnico (hoje)
        por_tecnico = VistoriaService.group_by_technician(hoje)

        return render_template('vistorias/agenda.html',
                             vistorias_hoje=vistorias_hoje,
                             vistorias_atrasadas=vistorias_atrasadas,
                             proximas_vistorias=proximas_vistorias,
                             por_tecnico=por_tecnico)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar agenda: {str(e)}")
        flash('Erro ao carregar agenda', 'error')
        return redirect(url_for('vistoria.index'))

@vistoria_bp.route('/relatorio')
@login_required
@require_role(2)
def relatorio():
    """Relatório de vistorias"""
    try:
        # Parâmetros do relatório
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo = request.args.get('tipo')
        tecnico_id = request.args.get('tecnico_id', type=int)
        status = request.args.get('status')

        # Gerar relatório
        dados = VistoriaService.generate_report(
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo=tipo,
            tecnico_id=tecnico_id,
            status=status
        )

        # Dados para filtros
        tecnicos = UserService.get_technicians()
        tipos = VistoriaService.get_tipos()

        return render_template('vistorias/relatorio.html',
                             dados=dados,
                             tecnicos=tecnicos,
                             tipos=tipos)

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório: {str(e)}")
        flash('Erro ao gerar relatório', 'error')
        return redirect(url_for('vistoria.index'))

@vistoria_bp.route('/api/por-ordem/<int:ordem_id>')
@login_required
def api_por_ordem(ordem_id):
    """API para buscar vistorias por ordem de serviço"""
    try:
        vistorias = VistoriaService.get_by_ordem_servico(ordem_id)

        return jsonify([{
            'id': v.id,
            'tipo': v.tipo,
            'data_vistoria': v.data_vistoria.isoformat(),
            'status': v.status,
            'tecnico': v.tecnico.nome if v.tecnico else None
        } for v in vistorias])

    except Exception as e:
        current_app.logger.error(f"Erro ao buscar vistorias: {str(e)}")
        return jsonify([])

@vistoria_bp.route('/api/agenda/<date>')
@login_required
def api_agenda(date):
    """API para obter vistorias de uma data específica"""
    try:
        data_obj = datetime.strptime(date, '%Y-%m-%d').date()
        vistorias = VistoriaService.get_by_date(data_obj)

        return jsonify([{
            'id': v.id,
            'titulo': f"{v.tipo.title()} - {v.arvore.especie.nome_popular}",
            'hora': v.data_vistoria.strftime('%H:%M') if isinstance(v.data_vistoria, datetime) else '08:00',
            'tecnico': v.tecnico.nome if v.tecnico else 'Não atribuído',
            'status': v.status,
            'endereco': v.arvore.endereco or 'Endereço não informado'
        } for v in vistorias])

    except ValueError:
        return jsonify({'error': 'Data inválida'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar agenda: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500