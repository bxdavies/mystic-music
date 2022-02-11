from flask import Flask, current_app
from flask_mongoengine import MongoEngine
from flask_session import Session
from config import config

db = MongoEngine()
sess = Session()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    sess.init_app(app)

    from . account import account as accountBlueprint
    app.register_blueprint(accountBlueprint, url_prefix='/account')

    from . main import main as mainBlueprint
    app.register_blueprint(mainBlueprint)

   

    return app

