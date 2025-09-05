from models.requerimento_model import Requerimento
from models.requerente_model import Requerente
from models.arvore_model import Arvore
from models.user_model import User
from core.exceptions import ValidationError, NotFoundError
from sqlalchemy import or_

class RequerimentoService:
    """Serviço de gerenciamento de requerimentos"""

    @staticmethod
    def create(data):
        """Cria novo requerimento - data é dict com campos"""
        requerente_id = data.get('requerente_id')
        arvore_id = data.get('arvore_id')
        usuario_id = data.get('created_by')
        tipo = data.get('tipo')
        descricao = data.get('justificativa')
        observacoes = data.get('observacoes')

        if not all([requerente_id, arvore_id, usuario_id, tipo, descricao]):
            raise ValidationError("Todos os campos obrigatórios devem ser preenchidos")

        if tipo not in ['poda', 'remocao', 'transplante']:
            raise ValidationError("Tipo deve ser: poda, remoção ou transplante")

        if not Requerente.query.get(requerente_id):
            raise ValidationError("Requerente não encontrado")

        if not Arvore.query.get(arvore_id):
            raise ValidationError("Árvore não encontrada")

        if not User.query.get(usuario_id):
            raise ValidationError("Usuário não encontrado")

        numero = Requerimento.generate_numero()
        requerimento = Requerimento(
            numero=numero,
            requerente_id=requerente_id,
            arvore_id=arvore_id,
            criado_por=usuario_id,
            tipo=tipo,
            motivo=descricao,
            observacao=observacoes,
            status='pendente',
            data_abertura=None
        )
        return requerimento.save()

    @staticmethod
    def update(requerimento_id, data):
        requerimento = Requerimento.query.get(requerimento_id)
        if not requerimento:
            raise NotFoundError("Requerimento não encontrado")

        if not requerimento.pode_editar:
            raise ValidationError("Requerimento não pode ser editado neste status")

        for key, value in data.items():
            if hasattr(requerimento, key) and key not in ['id', 'numero', 'data_abertura']:
                setattr(requerimento, key, value)

        return requerimento.save()

    @staticmethod
    def get_by_id(requerimento_id):
        requerimento = Requerimento.query.get(requerimento_id)
        if not requerimento:
            raise NotFoundError("Requerimento não encontrado")
        return requerimento

    @staticmethod
    def can_edit(requerimento_id):
        requerimento = Requerimento.query.get(requerimento_id)
        return requerimento and requerimento.pode_editar

    @staticmethod
    def search(term, limit=50):
        query = Requerimento.query
        if term and len(term) >= 2:
            ilike_term = f"%{term}%"
            query = query.filter(
                or_(
                    Requerimento.numero.ilike(ilike_term),
                    Requerimento.tipo.ilike(ilike_term),
                    Requerimento.status.ilike(ilike_term),
                    Requerimento.motivo.ilike(ilike_term),
                    Requerimento.observacao.ilike(ilike_term),
                    Requerimento.prioridade.ilike(ilike_term)
                )
            )
        # Se o termo estiver vazio, retorna todos (limitados)
        return query.order_by(Requerimento.data_abertura.desc()).limit(limit).all()
    
    @staticmethod
    def get_paginated(page=1, per_page=10, status=None, tipo=None, requerente_id=None,
                      data_inicio=None, data_fim=None, search=None):
        query = Requerimento.query

        if status:
            query = query.filter_by(status=status)

        if tipo:
            query = query.filter_by(tipo=tipo)

        if requerente_id:
            query = query.filter_by(requerente_id=requerente_id)

        if data_inicio:
            query = query.filter(Requerimento.data_abertura >= data_inicio)

        if data_fim:
            query = query.filter(Requerimento.data_abertura <= data_fim)

        if search:
            ilike_query = f"%{search}%"
            query = query.filter(Requerimento.numero.ilike(ilike_query))

        return query.order_by(Requerimento.data_abertura.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_tipos():
        return ['poda', 'remocao', 'transplante']

    @staticmethod
    def get_status_list():
        return ['pendente', 'aprovado', 'negado', 'concluido']

    @staticmethod
    def get_statistics():
        """Retorna estatísticas dos requerimentos"""
        return {
            'total': Requerimento.query.count(),
            'pendentes': Requerimento.query.filter_by(status='aberto').count(),
            'aprovados': Requerimento.query.filter_by(status='aprovado').count(),
            'negados': Requerimento.query.filter_by(status='negado').count(),
            'concluidos': Requerimento.query.filter_by(status='concluido').count()
        }
    
    # Adicione outros métodos conforme necessidade, por exemplo approve, reject etc.
