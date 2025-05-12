from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from config import DevelopmentConfig, ProductionConfig
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import os
import sys

db = SQLAlchemy()
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
    
    return app

def create_database(app : Flask) -> None:
    with app.app_context():
        from app.modals import Users, Products, Category
        db.create_all()
        print("Created Database!")