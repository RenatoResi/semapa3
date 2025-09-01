from models.requerente_model import Requerente
from core.exceptions import ValidationError, NotFoundError
from sqlalchemy import or_

class RequerenteService:
    """Serviço de gerenciamento de requerentes"""

    @staticmethod
    def create(nome, telefone=None, observacao=None):
        if not all([nome]):
            raise ValidationError("Nome é um campo obrigatório")

        requerente = Requerente(
            nome=nome,
            telefone=telefone,
            observacao=observacao
        )
        return requerente.save()

    @staticmethod
    def update(requerente_id, **kwargs):
        requerente = Requerente.query.get(requerente_id)
        if not requerente:
            raise NotFoundError("Requerente não encontrado")

        for key, value in kwargs.items():
            if hasattr(requerente, key):
                setattr(requerente, key, value)

        return requerente.save()

    @staticmethod
    def delete(requerente_id):
        requerente = Requerente.query.get(requerente_id)
        if not requerente:
            raise NotFoundError("Requerente não encontrado")

        if requerente.total_requerimentos > 0:
            raise ValidationError("Não é possível remover requerente com requerimentos")

        requerente.delete()
        return True

    @staticmethod
    def get_by_id(requerente_id):
        requerente = Requerente.query.get(requerente_id)
        if not requerente:
            raise NotFoundError("Requerente não encontrado")
        return requerente

    @staticmethod
    def search(query, page=1, per_page=10):
        """Busca requerentes com paginação e case-insensitive"""

        if query:
            ilike_query = f"%{query}%"
            requerentes = Requerente.query.filter(
                or_(
                    Requerente.nome.ilike(ilike_query),
                    Requerente.telefone.ilike(ilike_query),
                    Requerente.observacao.ilike(ilike_query)
                )
            ).order_by(Requerente.nome).all()
        else:
            requerentes = Requerente.query.order_by(Requerente.nome).all()

        start = (page - 1) * per_page
        end = start + per_page
        return requerentes[start:end], len(requerentes)

    @staticmethod
    def get_all(page=1, per_page=10):
        pagination = Requerente.query.order_by(Requerente.nome).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination.items, pagination.total
