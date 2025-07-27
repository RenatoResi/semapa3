from models.vistoria_model import Vistoria
from core.database import db
from utils.helpers import handle_upload
from utils.validators import validate_vistoria

class VistoriaService:
    @staticmethod
    def list_by_ordem_servico(ordem_id):
        return Vistoria.query.filter_by(ordem_servico_id=ordem_id).all()

    @staticmethod
    def create(data, files):
        validate_vistoria(data)
        vistoria = Vistoria(**data)
        db.session.add(vistoria)
        db.session.commit()
        if files:
            handle_upload(files, vistoria.id, 'vistoria')
        return vistoria

    @staticmethod
    def update(vistoria_id, data):
        vistoria = Vistoria.query.get_or_404(vistoria_id)
        for key, value in data.items():
            setattr(vistoria, key, value)
        db.session.commit()
        return vistoria

    @staticmethod
    def delete(vistoria_id):
        vistoria = Vistoria.query.get_or_404(vistoria_id)
        db.session.delete(vistoria)
        db.session.commit()
