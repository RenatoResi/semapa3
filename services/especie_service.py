from models.especie_model import Especie
from core.database import db
from utils.validators import validate_especie

class EspecieService:
    @staticmethod
    def list_all():
        return Especie.query.order_by(Especie.nome_cientifico).all()

    @staticmethod
    def create(data):
        validate_especie(data)
        especie = Especie(**data)
        db.session.add(especie)
        db.session.commit()
        return especie

    @staticmethod
    def update(especie_id, data):
        especie = Especie.query.get_or_404(especie_id)
        for key, value in data.items():
            setattr(especie, key, value)
        db.session.commit()
        return especie

    @staticmethod
    def delete(especie_id):
        especie = Especie.query.get_or_404(especie_id)
        db.session.delete(especie)
        db.session.commit()
