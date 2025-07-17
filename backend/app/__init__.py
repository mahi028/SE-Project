from flask import Flask, request
from flask_cors import CORS
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_graphql import GraphQLView
from config import DevelopmentConfig, ProductionConfig
import chromadb
import insightface
from .graphql import schema
from .models import db
from .graphql.auth import jwt
import os
import sys

migration = Migrate()
csrf = CSRFProtect()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
face_collection = chroma_client.get_or_create_collection(
    name="face_embeddings",
    metadata={"hnsw:space": "cosine"}
)

face_model = insightface.app.FaceAnalysis(name='buffalo_l')
face_model.prepare(ctx_id=0)  # set to -1 if using CPU


def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), "static"),
                )
                
    app.config.from_object(DevelopmentConfig) #Change DevelopmentConfig to ProductionConfig in production
    CORS(app, origins=['*'], supports_credentials=True)

    db.init_app(app)
    migration.init_app(app, db, render_as_batch=True)

    app.app_context().push()

    csrf.init_app(app)
    jwt.init_app(app)

    from app.api.user_lookup import lookup
    app.register_blueprint(lookup, url_prefix='/user-lookup')

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )
    
    return app
