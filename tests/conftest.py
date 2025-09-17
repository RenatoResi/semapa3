import pytest
from app import create_app
from core.database import db as _db
from config.settings import Settings

class TestConfig(Settings):
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/semapa_test'
    TESTING = True

@pytest.fixture(scope='session')
def app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    return _db
