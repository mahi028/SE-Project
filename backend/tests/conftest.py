import sys
import os
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

# Make sure app/ is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import db as _db
from app.graphql.auth import AuthMutation
from app.graphql.users import UsersQuery, UsersMutation
import graphene
from flask_graphql import GraphQLView


@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"

    _db.init_app(app)
    JWTManager(app)

    class Mutation(AuthMutation, UsersMutation, graphene.ObjectType):
        pass

    class Query(UsersQuery, graphene.ObjectType):
        pass

    schema = graphene.Schema(query=Query, mutation=Mutation)

    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=False)
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(autouse=True)
def run_before_each_test(app):
    with app.app_context():
        _db.drop_all()
        _db.create_all()

@pytest.fixture
def client(app):
    return app.test_client()
