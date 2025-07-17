from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, JWTManager, set_access_cookies
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..utils.hash import checkpw, hashpw
from ..utils.dbUtils import adddb, commitdb, generate_ez_id
from ..models import User, Roles
import graphene
from .return_types import ReturnType
from datetime import datetime
jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.ez_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):        
    identity = jwt_data["sub"]
    return User.query.get(identity)


class AuthTokenType(graphene.ObjectType):
    token = graphene.String()
    message = graphene.String()
    status = graphene.Int()


class GetToken(graphene.ObjectType):
    get_token = graphene.Field(AuthTokenType, ez_id=graphene.String(), password=graphene.String())
    def resolve_get_token(self, info, password, ez_id=None, email=None):
        if ez_id:
            user = User.query.get(ez_id)
        elif email:
            user = User.query.filter(User.email == email).first()
        else:
            return AuthTokenType(token=None, message="No user found", status=404)
        
        if user:
            if checkpw(password, user.password):
                access_token = create_access_token(identity=user)
                return AuthTokenType(token = access_token)


class Register(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        role = graphene.Int(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        name = graphene.String(required=True)
        phone_num = graphene.String(required=True)

    Output = ReturnType

    def mutate(root, info, email, role, password, confirm_password, name, phone_num):
        if email is None or role is None or password is None or confirm_password is None:
            return ReturnType(status=400, message="Insufficient information.")

        if role not in [1, 0]:
            return ReturnType(status=402, message="Role must be either Senior Citizen (0) or Health Professional (1).")

        if password != confirm_password:
            return ReturnType(status=403, message="Passwords do not match.")

        if User.query.filter_by(email=email).first():
            return ReturnType(status=409, message="User with the given email already exists.")

        try:
            ez_id = generate_ez_id(role)
            new_user = User(
                ez_id=ez_id,
                role=role,
                email=email,
                password=hashpw(password),  # assuming hashpw is defined
                name=name,
                phone_num=phone_num,
            )
            adddb(new_user)  # assuming adddb is defined
            commitdb()       # assuming commitdb is defined
        except Exception as err:
            print(err)
            return ReturnType(status=500, message="Something went wrong. Please try again.")

        return ReturnType(status=200, message="Registration successful.")
    
class AuthMutation(graphene.ObjectType):
    register = Register.Field()
    get_token = GetToken.Field()
