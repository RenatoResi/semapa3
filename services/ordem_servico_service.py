from models.ordem_model import OrdemServico
from core.database import db
from utils.validators import validate_ordem_servico

class OrdemServicoService:
    @staticmethod
    def list_all(status=None):
        query = OrdemServico.query
        if status:
            query = query.filter_by(status=status)
        return query.all()

    @staticmethod
    def create(data):
        validate_ordem_servico(data)
        ordem = OrdemServico(**data)
        db.session.add(ordem)
        db.session.commit()
        return ordem

    @staticmethod
    def update(ordem_id, data):
        ordem = OrdemServico.query.get_or_404(ordem_id)
        for key, value in data.items():
            setattr(ordem, key, value)
        db.session.commit()
        return ordem

    @staticmethod
    def concluir(ordem_id):
        ordem = OrdemServico.query.get_or_404(ordem_id)
        ordem.status = 'concluida'
        db.session.commit()
