import pytest

from app.__init__ import create_app
from app.extensions import db, bcrypt
from app.models.models import User
from config import TestConfig


@pytest.fixture()
def app():
    app=create_app(config_class=TestConfig)
    
    ctx=app.app_context()
    ctx.push()

    with ctx:
        db.create_all()
        admin=User(username='admin', password=bcrypt.generate_password_hash('password'), role='admin')
        db.session.add(admin)
        db.session.commit()

    yield app
    db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
