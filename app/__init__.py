import os
from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.urandom(24)
    # Register blueprints (routes are defined in routes.py)
    from . import routes
    app.register_blueprint(routes.bp)
    return app
