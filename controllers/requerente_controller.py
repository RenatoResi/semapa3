from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from core.security import require_role
from services.requerente_service import RequerenteService

requerente_bp = Blueprint('requerente', __name__, url_prefix='/requerentes')

@requerente_bp.route('/')
@login_required
@require_role(1)
def index():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
        search = request.args.get('search', '').strip()

        if search:
            requerentes, total = RequerenteService.search(search, page=page, per_page=per_page)
        else:
            requerentes, total = RequerenteService.get_all(page=page, per_page=per_page)

        total_pages = (total + per_page - 1) // per_page

    except Exception as e:
        current_app.logger.error(f"Erro ao listar requerentes: {str(e)}")
        flash('Ocorreu um erro ao carregar a lista de requerentes. Tente novamente mais tarde.', 'error')
        requerentes = []
        total = 0
        total_pages = 0

    return render_template(
        'requerentes/list.html',
        requerentes=requerentes,
        page=page,
        total_pages=total_pages,
        total=total,
        search=search
    )

@requerente_bp.route('/novo')
@login_required
@require_role(1)
def novo():
    return render_template('requerentes/form.html', requerente=None)

@requerente_bp.route('/criar', methods=['POST'])
@login_required
@require_role(1)
def criar():
    try:
        data = {
            'nome': request.form.get('nome', '').strip(),
            'telefone': request.form.get('telefone', '').strip(),
            'observacao': request.form.get('observacao', '').strip(),
            'created_by': current_user.id
        }

        error = False
        if not data['nome']:
            flash('Nome é obrigatório', 'error')
            error = True

        if error:
            return render_template('requerentes/form.html', requerente=data), 400

        requerente = RequerenteService.create(data['nome'], data['telefone'], data['observacao'])

        flash('Requerente cadastrado com sucesso!', 'success')
        return redirect(url_for('requerente.detail', id=requerente.id))

    except Exception as e:
        current_app.logger.error(f"Erro ao criar requerente: {str(e)}")
        flash('Erro ao cadastrar requerente', 'error')
        return render_template('requerentes/form.html', requerente=data), 500

@requerente_bp.route('/<int:id>')
@login_required
@require_role(1)
def detail(id):
    try:
        requerente = RequerenteService.get_by_id(id)
        if not requerente:
            flash('Requerente não encontrado', 'error')
            return redirect(url_for('requerente.index'))

        return render_template('requerentes/detail.html', requerente=requerente)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar requerente {id}: {str(e)}")
        flash('Erro ao carregar requerente', 'error')
        return redirect(url_for('requerente.index'))

@requerente_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@require_role(1)
def edit(id):
    try:
        requerente = RequerenteService.get_by_id(id)
        if not requerente:
            flash('Requerente não encontrado', 'error')
            return redirect(url_for('requerente.index'))

        if request.method == 'POST':
            print(request.form)
            nome = request.form.get('nome', '').strip()
            telefone = request.form.get('telefone', '').strip()
            observacao = request.form.get('observacao', '').strip()

            if not nome:
                flash('Nome é obrigatório', 'error')
                return render_template('requerentes/form.html', requerente=requerente), 400

            try:
                RequerenteService.update(
                    requerente_id=id,
                    nome=nome,
                    telefone=telefone,
                    observacao=observacao
                )
                flash('Requerente atualizado com sucesso!', 'success')
                return redirect(url_for('requerente.detail', id=id))
            except Exception as e:
                current_app.logger.error(f"Erro ao atualizar requerente {id}: {str(e)}")
                flash('Erro ao atualizar requerente', 'error')
                return render_template('requerentes/form.html', requerente=requerente), 500

        # GET: exibe o formulário preenchido
        return render_template('requerentes/form.html', requerente=requerente)

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar requerente {id} para edição: {str(e)}")
        flash('Erro ao carregar requerente para edição', 'error')
        return redirect(url_for('requerente.index'))

@requerente_bp.route('/search')
@login_required
@require_role(1)
def search_api():
    query = request.args.get('search', '').strip()
    try:
        if query:
            requerentes, total = RequerenteService.search(query, page=1, per_page=50)
        else:
            requerentes, total = RequerenteService.get_all(page=1, per_page=50)

        result = [{
            'id': r.id,
            'nome': r.nome,
            'telefone': r.telefone,
            'observacao': r.observacao
        } for r in requerentes]

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Erro na busca AJAX: {e}")
        return jsonify([]), 500
