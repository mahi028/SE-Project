import sys
import os
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

# Make sure app/ is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import db as _db, User
from app.graphql.auth import AuthMutation, GetToken, AuthenticatedGraphQLView
from app.graphql.users import UsersQuery, UsersMutation
from app.graphql.seniors import SeniorsQuery, SeniorsMutation 
from app.graphql.doctors import DoctorsQuery, DoctorMutation
from app.graphql.appointments import AppointmentsQuery, AppointmentsMutation
from app.graphql.doc_reviews import DocReviewsQuery, DocReviewMutation
from app.graphql.emergency_contacts import EmergencyContactsQuery, EmergencyContactMutation
from app.graphql.groups import GroupQuery, GroupMutation  
from app.graphql.prescriptions import PrescriptionsQuery, PrescriptionsMutation
from app.graphql.vital_types import VitalTypesQuery, VitalTypesMutation
from app.graphql.vital_logs import VitalLogsQuery, VitalLogsMutation
from app.graphql.hospitals import HospitalsQuery, HospitalsMutation
import graphene

@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"

    _db.init_app(app)
    
    jwt = JWTManager()
    jwt.init_app(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.ez_id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):        
        identity = jwt_data["sub"]
        return User.query.get(identity)

    # Include SeniorsMutation in the Mutation class
    class Mutation(AuthMutation, UsersMutation, SeniorsMutation, DoctorMutation,AppointmentsMutation,DocReviewMutation,EmergencyContactMutation,GroupMutation,PrescriptionsMutation,VitalLogsMutation,VitalTypesMutation,HospitalsMutation, graphene.ObjectType):
        pass

    # Include SeniorsQuery in the Query class
    class Query(UsersQuery, GetToken, SeniorsQuery,DoctorsQuery,AppointmentsQuery,DocReviewsQuery,EmergencyContactsQuery,GroupQuery,PrescriptionsQuery,VitalLogsQuery,VitalTypesQuery,HospitalsQuery, graphene.ObjectType):
        pass

    schema = graphene.Schema(query=Query, mutation=Mutation)

    # Create a custom view class that properly sets up context
    class TestGraphQLView(AuthenticatedGraphQLView):
        def get_context(self):
            from flask import request
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            
            context = {"request": request}
            
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                context["current_user"] = user_id
            except Exception:
                context["current_user"] = None
            
            return context

    app.add_url_rule(
        "/graphql",
        view_func=TestGraphQLView.as_view("graphql", schema=schema, graphiql=False)
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

@pytest.fixture
def db_user(app):
    return User
