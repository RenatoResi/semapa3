from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from core.security import require_role
from services.especie_service import EspecieService
from utils.validators import validate_required_fields
from utils.helpers import allowed_file, save_uploaded_file

especie_bp = Blueprint('especie', __name__, url_prefix='/especies')

@especie_bp.route('/')
@login_required
@require_role(1)
def index():
    """Lista todas as espécies"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
        search = request.args.get('search', '').strip()

        especies = EspecieService.get_paginated(
            page=page,
            per_page=per_page,
            search=search
        )

        return render_template('especies/index.html', especies=especies)

    except Exception as e:
        current_app.logger.error(f"Erro ao listar espécies: {str(e)}")
        flash('Erro ao carregar lista de espécies', 'error')
        return render_template('especies/index.html', especies=None)

@especie_bp.route('/nova')
@login_required
@require_role(2)
def nova():
    """Formulário para nova espécie"""
    return render_template('especies/form.html', especie=None)

@especie_bp.route('/criar', methods=['POST'])
@login_required
@require_role(2)
def criar():
    """Cria nova espécie"""
    try:
        # Validar campos obrigatórios
        required_fields = ['nome_cientifico', 'nome_popular']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('especie.nova'))

        # Verificar se já existe espécie com mesmo nome científico
        nome_cientifico = request.form['nome_cientifico'].strip()
        if EspecieService.exists_by_nome_cientifico(nome_cientifico):
            flash('Já existe uma espécie com este nome científico', 'error')
            return redirect(url_for('especie.nova'))

        # Dados da espécie
        data = {
            'nome_cientifico': nome_cientifico,
            'nome_popular': request.form['nome_popular'].strip(),
            'familia': request.form.get('familia', '').strip(),
            'origem': request.form.get('origem', '').strip(),
            'porte': request.form.get('porte', '').strip(),
            'copa': request.form.get('copa', '').strip(),
            'folhagem': request.form.get('folhagem', '').strip(),
            'florescimento': request.form.get('florescimento', '').strip(),
            'frutificacao': request.form.get('frutificacao', '').strip(),
            'observacoes': request.form.get('observacoes', '').strip(),
            'created_by': current_user.id
        }

        # Processar upload de foto
        foto = request.files.get('foto')
        if foto and foto.filename and allowed_file(foto.filename):
            data['foto_url'] = save_uploaded_file(foto, 'especies')

        # Criar espécie
        especie = EspecieService.create(data)

        flash('Espécie cadastrada com sucesso!', 'success')
        return redirect(url_for('especie.detalhes', id=especie.id))

    except Exception as e:
        current_app.logger.error(f"Erro ao criar espécie: {str(e)}")
        flash('Erro ao cadastrar espécie', 'error')
        return redirect(url_for('especie.nova'))

@especie_bp.route('/<int:id>')
@login_required
@require_role(1)
def detalhes(id):
    """Exibe detalhes de uma espécie"""
    try:
        especie = EspecieService.get_by_id(id)
        if not especie:
            flash('Espécie não encontrada', 'error')
            return redirect(url_for('especie.index'))

        # Estatísticas da espécie
        stats = EspecieService.get_statistics(id)

        return render_template('especies/detalhes.html', especie=especie, stats=stats)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar espécie {id}: {str(e)}")
        flash('Erro ao carregar detalhes da espécie', 'error')
        return redirect(url_for('especie.index'))

@especie_bp.route('/<int:id>/editar')
@login_required
@require_role(2)
def editar(id):
    """Formulário para editar espécie"""
    try:
        especie = EspecieService.get_by_id(id)
        if not especie:
            flash('Espécie não encontrada', 'error')
            return redirect(url_for('especie.index'))

        return render_template('especies/form.html', especie=especie)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de edição: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('especie.index'))

@especie_bp.route('/<int:id>/atualizar', methods=['POST'])
@login_required
@require_role(2)
def atualizar(id):
    """Atualiza uma espécie"""
    try:
        especie = EspecieService.get_by_id(id)
        if not especie:
            flash('Espécie não encontrada', 'error')
            return redirect(url_for('especie.index'))

        # Validar campos obrigatórios
        required_fields = ['nome_cientifico', 'nome_popular']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('especie.editar', id=id))

        # Verificar se já existe outra espécie com mesmo nome científico
        nome_cientifico = request.form['nome_cientifico'].strip()
        if EspecieService.exists_by_nome_cientifico(nome_cientifico, exclude_id=id):
            flash('Já existe uma espécie com este nome científico', 'error')
            return redirect(url_for('especie.editar', id=id))

        # Dados para atualização
        data = {
            'nome_cientifico': nome_cientifico,
            'nome_popular': request.form['nome_popular'].strip(),
            'familia': request.form.get('familia', '').strip(),
            'origem': request.form.get('origem', '').strip(),
            'porte': request.form.get('porte', '').strip(),
            'copa': request.form.get('copa', '').strip(),
            'folhagem': request.form.get('folhagem', '').strip(),
            'florescimento': request.form.get('florescimento', '').strip(),
            'frutificacao': request.form.get('frutificacao', '').strip(),
            'observacoes': request.form.get('observacoes', '').strip(),
            'updated_by': current_user.id
        }

        # Processar upload de nova foto
        foto = request.files.get('foto')
        if foto and foto.filename and allowed_file(foto.filename):
            data['foto_url'] = save_uploaded_file(foto, 'especies')

        # Atualizar espécie
        EspecieService.update(id, data)

        flash('Espécie atualizada com sucesso!', 'success')
        return redirect(url_for('especie.detalhes', id=id))

    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar espécie {id}: {str(e)}")
        flash('Erro ao atualizar espécie', 'error')
        return redirect(url_for('especie.editar', id=id))

@especie_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
@require_role(3)
def excluir(id):
    """Exclui uma espécie"""
    try:
        especie = EspecieService.get_by_id(id)
        if not especie:
            flash('Espécie não encontrada', 'error')
            return redirect(url_for('especie.index'))

        # Verificar se espécie pode ser excluída
        if not EspecieService.can_delete(id):
            flash('Espécie não pode ser excluída pois possui árvores cadastradas', 'error')
            return redirect(url_for('especie.detalhes', id=id))

        EspecieService.delete(id)
        flash('Espécie excluída com sucesso!', 'success')
        return redirect(url_for('especie.index'))

    except Exception as e:
        current_app.logger.error(f"Erro ao excluir espécie {id}: {str(e)}")
        flash('Erro ao excluir espécie', 'error')
        return redirect(url_for('especie.detalhes', id=id))

@especie_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar espécies (AJAX)"""
    try:
        term = request.args.get('term', '').strip()
        limit = request.args.get('limit', 10, type=int)

        if len(term) < 2:
            return jsonify([])

        especies = EspecieService.search(term, limit)

        return jsonify([{
            'id': e.id,
            'label': f"{e.nome_cientifico} ({e.nome_popular})",
            'value': e.id,
            'nome_cientifico': e.nome_cientifico,
            'nome_popular': e.nome_popular
        } for e in especies])

    except Exception as e:
        current_app.logger.error(f"Erro na busca de espécies: {str(e)}")
        return jsonify([])

@especie_bp.route('/api/info/<int:id>')
@login_required
def api_info(id):
    """API para obter informações de uma espécie"""
    try:
        especie = EspecieService.get_by_id(id)
        if not especie:
            return jsonify({'error': 'Espécie não encontrada'}), 404

        return jsonify({
            'id': especie.id,
            'nome_cientifico': especie.nome_cientifico,
            'nome_popular': especie.nome_popular,
            'familia': especie.familia,
            'origem': especie.origem,
            'porte': especie.porte,
            'copa': especie.copa,
            'folhagem': especie.folhagem,
            'florescimento': especie.florescimento,
            'frutificacao': especie.frutificacao,
            'foto_url': especie.foto_url
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter informações da espécie: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@especie_bp.route('/relatorio')
@login_required
@require_role(2)
def relatorio():
    """Relatório de espécies"""
    try:
        # Estatísticas gerais
        total_especies = EspecieService.count_all()
        especies_com_arvores = EspecieService.count_with_trees()
        especies_sem_arvores = total_especies - especies_com_arvores

        # Top espécies por número de árvores
        top_especies = EspecieService.get_top_by_trees(10)

        # Espécies por origem
        especies_por_origem = EspecieService.group_by_origin()

        # Espécies por porte
        especies_por_porte = EspecieService.group_by_size()

        return render_template('especies/relatorio.html',
                             total_especies=total_especies,
                             especies_com_arvores=especies_com_arvores,
                             especies_sem_arvores=especies_sem_arvores,
                             top_especies=top_especies,
                             especies_por_origem=especies_por_origem,
                             especies_por_porte=especies_por_porte)

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatório de espécies: {str(e)}")
        flash('Erro ao gerar relatório', 'error')
        return redirect(url_for('especie.index'))