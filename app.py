import os

from flask import Flask
from db.session import generate_db_conn_string
from views import init_views
from controllers import init_controllers


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = generate_db_conn_string()
    app.secret_key = os.environ['SECRET_KEY']

    # Initialize controllers from controllers.py (scheduling & email functionality)
    init_controllers(app)

    # Initialize routes from views.py. Could use blueprints instead.
    init_views(app)

    return app
