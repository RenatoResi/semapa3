# -*- coding: utf-8 -*-
"""
SEMAPA3 - Arvore Service
Serviço de gerenciamento de árvores
"""

from models.arvore_model import Arvore
from models.especie_model import Especie
from core.exceptions import ValidationError, NotFoundError

class ArvoreService:
    """Serviço de gerenciamento de árvores"""

    @staticmethod
    def create(numero, especie_id, endereco, **kwargs):
        """Cria nova árvore"""
        if not all([numero, especie_id, endereco]):
            raise ValidationError("Número, espécie e endereço são obrigatórios")

        # Validar se número já existe
        if Arvore.find_by_numero(numero):
            raise ValidationError("Número de árvore já cadastrado")

        # Validar se espécie existe
        especie = Especie.query.get(especie_id)
        if not especie:
            raise ValidationError("Espécie não encontrada")

        arvore = Arvore(
            numero=numero,
            especie_id=especie_id,
            endereco=endereco,
            **kwargs
        )
        return arvore.save()

    @staticmethod
    def update(arvore_id, **kwargs):
        """Atualiza dados da árvore"""
        arvore = Arvore.query.get(arvore_id)
        if not arvore:
            raise NotFoundError("Árvore não encontrada")

        # Validar espécie se fornecida
        if 'especie_id' in kwargs:
            especie = Especie.query.get(kwargs['especie_id'])
            if not especie:
                raise ValidationError("Espécie não encontrada")

        # Atualizar campos
        for key, value in kwargs.items():
            if hasattr(arvore, key):
                setattr(arvore, key, value)

        return arvore.save()

    @staticmethod
    def delete(arvore_id):
        """Remove árvore"""
        arvore = Arvore.query.get(arvore_id)
        if not arvore:
            raise NotFoundError("Árvore não encontrada")

        # Verificar se tem requerimentos
        if arvore.total_requerimentos > 0:
            raise ValidationError("Não é possível remover árvore com requerimentos")

        arvore.delete()
        return True

    @staticmethod
    def get_by_id(arvore_id):
        """Busca árvore por ID"""
        arvore = Arvore.query.get(arvore_id)
        if not arvore:
            raise NotFoundError("Árvore não encontrada")
        return arvore

    @staticmethod
    def search(query, page=1, per_page=10):
        """Busca árvores com paginação"""
        if query:
            arvores = Arvore.search(query)
        else:
            arvores = Arvore.query.order_by(Arvore.numero).all()

        # Paginação manual
        start = (page - 1) * per_page
        end = start + per_page
        return arvores[start:end], len(arvores)

    @staticmethod
    def get_with_coordinates():
        """Retorna árvores com coordenadas para mapa"""
        return Arvore.query.filter(
            Arvore.latitude.isnot(None),
            Arvore.longitude.isnot(None)
        ).all()

    @staticmethod
    def generate_kml(arvores=None):
        """Gera arquivo KML das árvores"""
        if arvores is None:
            arvores = ArvoreService.get_with_coordinates()

        kml_data = []
        for arvore in arvores:
            if arvore.has_coordinates:
                kml_data.append(arvore.to_kml_dict())

        return kml_data
