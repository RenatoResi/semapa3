from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from core.security import require_role
from services.arvore_service import ArvoreService
from services.especie_service import EspecieService
from services.requerente_service import RequerenteService
from utils.validators import validate_coordinates, validate_required_fields
from utils.helpers import allowed_file, save_uploaded_file

arvore_bp = Blueprint('arvore', __name__, url_prefix='/arvores')

@arvore_bp.route('/')
@login_required
@require_role(1)
def index():
    """Lista todas as árvores"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

        # Filtros
        especie_id = request.args.get('especie_id', type=int)
        requerente_id = request.args.get('requerente_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search', '').strip()

        # Buscar árvores
        arvores = ArvoreService.get_paginated(
            page=page, 
            per_page=per_page,
            especie_id=especie_id,
            requerente_id=requerente_id,
            status=status,
            search=search
        )

        # Dados para filtros
        especies = EspecieService.get_all()
        requerentes = RequerenteService.get_all()

        return render_template('arvores/index.html', 
                             arvores=arvores, 
                             especies=especies,
                             requerentes=requerentes)

    except Exception as e:
        current_app.logger.error(f"Erro ao listar árvores: {str(e)}")
        flash('Erro ao carregar lista de árvores', 'error')
        return render_template('arvores/index.html', arvores=None)

@arvore_bp.route('/nova')
@login_required
@require_role(2)
def nova():
    """Formulário para nova árvore"""
    try:
        especies = EspecieService.get_all()
        requerentes = RequerenteService.get_all()

        return render_template('arvores/form.html', 
                             arvore=None, 
                             especies=especies,
                             requerentes=requerentes)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('arvore.index'))

@arvore_bp.route('/criar', methods=['POST'])
@login_required
@require_role(2)
def criar():
    """Cria nova árvore"""
    try:
        # Validar campos obrigatórios
        required_fields = ['especie_id', 'latitude', 'longitude']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('arvore.nova'))

        # Validar coordenadas
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        if not validate_coordinates(latitude, longitude):
            flash('Coordenadas inválidas', 'error')
            return redirect(url_for('arvore.nova'))

        # Dados da árvore
        data = {
            'especie_id': int(request.form['especie_id']),
            'requerente_id': int(request.form['requerente_id']) if request.form.get('requerente_id') else None,
            'latitude': latitude,
            'longitude': longitude,
            'altura': float(request.form['altura']) if request.form.get('altura') else None,
            'dap': float(request.form['dap']) if request.form.get('dap') else None,
            'observacoes': request.form.get('observacoes', '').strip(),
            'endereco': request.form.get('endereco', '').strip(),
            'bairro': request.form.get('bairro', '').strip(),
            'status': request.form.get('status', 'ativa'),
            'created_by': current_user.id
        }

        # Processar upload de foto
        foto = request.files.get('foto')
        if foto and foto.filename and allowed_file(foto.filename):
            data['foto_url'] = save_uploaded_file(foto, 'arvores')

        # Criar árvore
        arvore = ArvoreService.create(data)

        flash('Árvore cadastrada com sucesso!', 'success')
        return redirect(url_for('arvore.detalhes', id=arvore.id))

    except ValueError as e:
        flash(f'Dados inválidos: {str(e)}', 'error')
        return redirect(url_for('arvore.nova'))
    except Exception as e:
        current_app.logger.error(f"Erro ao criar árvore: {str(e)}")
        flash('Erro ao cadastrar árvore', 'error')
        return redirect(url_for('arvore.nova'))

@arvore_bp.route('/<int:id>')
@login_required
@require_role(1)
def detalhes(id):
    """Exibe detalhes de uma árvore"""
    try:
        arvore = ArvoreService.get_by_id(id)
        if not arvore:
            flash('Árvore não encontrada', 'error')
            return redirect(url_for('arvore.index'))

        return render_template('arvores/detalhes.html', arvore=arvore)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar árvore {id}: {str(e)}")
        flash('Erro ao carregar detalhes da árvore', 'error')
        return redirect(url_for('arvore.index'))

@arvore_bp.route('/<int:id>/editar')
@login_required
@require_role(2)
def editar(id):
    """Formulário para editar árvore"""
    try:
        arvore = ArvoreService.get_by_id(id)
        if not arvore:
            flash('Árvore não encontrada', 'error')
            return redirect(url_for('arvore.index'))

        especies = EspecieService.get_all()
        requerentes = RequerenteService.get_all()

        return render_template('arvores/form.html', 
                             arvore=arvore, 
                             especies=especies,
                             requerentes=requerentes)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de edição: {str(e)}")
        flash('Erro ao carregar formulário', 'error')
        return redirect(url_for('arvore.index'))

@arvore_bp.route('/<int:id>/atualizar', methods=['POST'])
@login_required
@require_role(2)
def atualizar(id):
    """Atualiza uma árvore"""
    try:
        arvore = ArvoreService.get_by_id(id)
        if not arvore:
            flash('Árvore não encontrada', 'error')
            return redirect(url_for('arvore.index'))

        # Validar campos obrigatórios
        required_fields = ['especie_id', 'latitude', 'longitude']
        if not validate_required_fields(request.form, required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('arvore.editar', id=id))

        # Validar coordenadas
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        if not validate_coordinates(latitude, longitude):
            flash('Coordenadas inválidas', 'error')
            return redirect(url_for('arvore.editar', id=id))

        # Dados para atualização
        data = {
            'especie_id': int(request.form['especie_id']),
            'requerente_id': int(request.form['requerente_id']) if request.form.get('requerente_id') else None,
            'latitude': latitude,
            'longitude': longitude,
            'altura': float(request.form['altura']) if request.form.get('altura') else None,
            'dap': float(request.form['dap']) if request.form.get('dap') else None,
            'observacoes': request.form.get('observacoes', '').strip(),
            'endereco': request.form.get('endereco', '').strip(),
            'bairro': request.form.get('bairro', '').strip(),
            'status': request.form.get('status', 'ativa'),
            'updated_by': current_user.id
        }

        # Processar upload de nova foto
        foto = request.files.get('foto')
        if foto and foto.filename and allowed_file(foto.filename):
            data['foto_url'] = save_uploaded_file(foto, 'arvores')

        # Atualizar árvore
        ArvoreService.update(id, data)

        flash('Árvore atualizada com sucesso!', 'success')
        return redirect(url_for('arvore.detalhes', id=id))

    except ValueError as e:
        flash(f'Dados inválidos: {str(e)}', 'error')
        return redirect(url_for('arvore.editar', id=id))
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar árvore {id}: {str(e)}")
        flash('Erro ao atualizar árvore', 'error')
        return redirect(url_for('arvore.editar', id=id))

@arvore_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
@require_role(3)
def excluir(id):
    """Exclui uma árvore"""
    try:
        arvore = ArvoreService.get_by_id(id)
        if not arvore:
            flash('Árvore não encontrada', 'error')
            return redirect(url_for('arvore.index'))

        # Verificar se árvore pode ser excluída
        if not ArvoreService.can_delete(id):
            flash('Árvore não pode ser excluída pois possui requerimentos associados', 'error')
            return redirect(url_for('arvore.detalhes', id=id))

        ArvoreService.delete(id)
        flash('Árvore excluída com sucesso!', 'success')
        return redirect(url_for('arvore.index'))

    except Exception as e:
        current_app.logger.error(f"Erro ao excluir árvore {id}: {str(e)}")
        flash('Erro ao excluir árvore', 'error')
        return redirect(url_for('arvore.detalhes', id=id))

@arvore_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar árvores (AJAX)"""
    try:
        term = request.args.get('term', '').strip()
        limit = request.args.get('limit', 10, type=int)

        if len(term) < 2:
            return jsonify([])

        arvores = ArvoreService.search(term, limit)

        return jsonify([{
            'id': a.id,
            'label': f"{a.especie.nome_cientifico} - {a.endereco or 'Sem endereço'}",
            'value': a.id,
            'latitude': float(a.latitude),
            'longitude': float(a.longitude)
        } for a in arvores])

    except Exception as e:
        current_app.logger.error(f"Erro na busca de árvores: {str(e)}")
        return jsonify([])

@arvore_bp.route('/api/coordenadas/<int:id>')
@login_required  
def api_coordenadas(id):
    """API para obter coordenadas de uma árvore"""
    try:
        arvore = ArvoreService.get_by_id(id)
        if not arvore:
            return jsonify({'error': 'Árvore não encontrada'}), 404

        return jsonify({
            'latitude': float(arvore.latitude),
            'longitude': float(arvore.longitude),
            'endereco': arvore.endereco,
            'especie': arvore.especie.nome_cientifico
        })

    except Exception as e:
        current_app.logger.error(f"Erro ao obter coordenadas: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500