from models.user_model import User
from core.database import db
from utils.validators import validate_user

class UserService:
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(data):
        validate_user(data)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user_id, data):
        user = User.query.get_or_404(user_id)
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def deactivate(user_id):
        user = User.query.get_or_404(user_id)
        user.is_active = False
        db.session.commit()
