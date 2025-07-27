from flask import Blueprint, jsonify, request, abort
from services.arvore_service import ArvoreService
from services.especie_service import EspecieService
from services.requerente_service import RequerenteService
from services.ordem_servico_service import OrdemServicoService
from services.vistoria_service import VistoriaService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Exemplo: Listar árvores (GET /api/arvores)
@api_bp.route('/arvores', methods=['GET'])
def get_arvores():
    arvores = ArvoreService.list_all()
    return jsonify([arvore.to_dict() for arvore in arvores])

# Exemplo: Detalhes de uma árvore
@api_bp.route('/arvores/<int:arvore_id>', methods=['GET'])
def get_arvore(arvore_id):
    arvore = ArvoreService.get_by_id(arvore_id)
    if not arvore:
        abort(404)
    return jsonify(arvore.to_dict())

# Exemplo: Listar espécies
@api_bp.route('/especies', methods=['GET'])
def get_especies():
    especies = EspecieService.list_all()
    return jsonify([esp.to_dict() for esp in especies])

# Listar requerentes
@api_bp.route('/requerentes', methods=['GET'])
def get_requerentes():
    requerentes = RequerenteService.list_all()
    return jsonify([req.to_dict() for req in requerentes])

# Listar ordens de serviço
@api_bp.route('/ordens', methods=['GET'])
def get_ordens():
    ordens = OrdemServicoService.list_all()
    return jsonify([o.to_dict() for o in ordens])

# Listar vistorias
@api_bp.route('/vistorias', methods=['GET'])
def get_vistorias():
    vistorias = VistoriaService.list_all()
    return jsonify([v.to_dict() for v in vistorias])

# Exemplo de POST para criar requerente (expandir conforme necessário)
@api_bp.route('/requerentes', methods=['POST'])
def post_requerente():
    data = request.get_json()
    requerente = RequerenteService.create(data)
    return jsonify(requerente.to_dict()), 201

# Adicione outros endpoints conforme necessário...

# No seu app/__init__.py ou aplicação principal:
# from controllers.api_controller import api_bp
# app.register_blueprint(api_bp)
