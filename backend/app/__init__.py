from flask import Flask, request
from flask_cors import CORS
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_graphql import GraphQLView
from config import DevelopmentConfig, ProductionConfig
from .api.graphql import schema
from .modals import db
import os
import sys

migration = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), "static"),
                )
                
    app.config.from_object(DevelopmentConfig) #Change DevelopmentConfig to ProductionConfig in production
    CORS(app, origins=['*'], supports_credentials=True)

    db.init_app(app)
    migration.init_app(app, db, render_as_batch=True)

    if sys.argv[-1] == 'init_db':
        create_database(app)

    app.app_context().push()

    csrf.init_app(app)

    from app.api import api
    api.init_app(app)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )
    
    return app

def create_database(app : Flask) -> None:
    with app.app_context():
        db.create_all()
        print("Created Database!")