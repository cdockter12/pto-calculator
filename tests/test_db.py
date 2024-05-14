import pytest
from flask_sqlalchemy import SQLAlchemy
from db.models import db


def test_get_close_db(app):
    with app.app_context():
        assert db is SQLAlchemy()

    with pytest.raises(SQLAlchemy.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('SQLALCHEMY().db.create_all()', fake_init_db)
    result = runner.invoke(args=['create-all'])
    assert 'Initialized' in result.output
    assert Recorder.called
