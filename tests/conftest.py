import os
import tempfile

import pytest
from app import create_app
from db.models import db


# Following link Here: https://flask.palletsprojects.com/en/3.0.x/tutorial/tests/

#Authentication
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
    })
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://' + db_path

    with app.app_context():
        db.create_all()
        db.engine.execute("""
        INSERT INTO users (email, password, is_senior)
        VALUES
            ('test@test.com', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 1),
            ('other@other.com', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', 0);

        INSERT INTO pto (user_id, pto_balance, last_updated, is_current)
        VALUES
            (1, 25 || -5 || 0, '2018-01-01 00:00:00', true);
            (2, 25 || -5 || 0, '2019-01-01 00:00:00', false);
        """)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()