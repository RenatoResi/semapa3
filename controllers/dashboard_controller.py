# -*- coding: utf-8 -*-
"""
SEMAPA3 - Dashboard Controller
Controller principal do dashboard
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from services.requerimento_service import RequerimentoService
from services.arvore_service import ArvoreService
from models import User, Requerente, Arvore, Especie, Requerimento, OrdemServico, Vistoria

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    # Estatísticas gerais
    stats = {
        'total_usuarios': User.query.count(),
        'total_requerentes': Requerente.query.count(),
        'total_arvores': Arvore.query.count(),
        'total_especies': Especie.query.count(),
    }

    # Estatísticas de requerimentos
    total_requerimentos = Requerimento.query.count()
    pendentes = Requerimento.query.filter(
        Requerimento.status.in_(["Aberto", "Pendente"])
    ).count()
    concluidos = Requerimento.query.filter_by(status="Concluído").count()
    negados = Requerimento.query.filter_by(status="Negado").count()

    req_stats = {
        "total": total_requerimentos,
        "pendentes": pendentes,
        "concluídos": concluidos,
        "negados": negados,
    }

    req_stats = RequerimentoService.get_statistics()

    # Últimos requerimentos
    ultimos_requerimentos = Requerimento.query.order_by(
        Requerimento.data_abertura.desc()
    ).limit(5).all()

    # ultimos_requerimentos = Requerimento.query.filter(
    #     Requerimento.status.in_(["aberto", "pendente"])
    # ).order_by(Requerimento.data_abertura.desc()).limit(5).all()

    # Ordens de serviço pendentes (tudo que não for concluído)
    ordens_pendentes = OrdemServico.query.filter(
        OrdemServico.status != "concluído"
    ).order_by(OrdemServico.data_emissao).limit(5).all()

    return render_template('dashboard/index.html',
                         stats=stats,
                         req_stats=req_stats,
                         ultimos_requerimentos=ultimos_requerimentos,
                         ordens_pendentes=ordens_pendentes)

@dashboard_bp.route('/map')
@login_required
def map_view():
    """Visualização em mapa"""
    arvores = ArvoreService.get_with_coordinates()
    return render_template('dashboard/map.html', arvores=arvores)

@dashboard_bp.route('/reports')
@login_required
def reports():
    """Relatórios do sistema"""
    return render_template('dashboard/reports.html')
