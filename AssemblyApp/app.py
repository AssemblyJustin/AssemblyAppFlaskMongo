from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_login import LoginManager

mongo = PyMongo()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from blueprints.auth.routes import auth
    from blueprints.main.routes import main
    from blueprints.cost_estimate import cost_estimate_bp

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(cost_estimate_bp, url_prefix='/cost_estimate')

    return app
