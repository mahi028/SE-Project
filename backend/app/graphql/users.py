from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, db
from .return_types import ReturnType

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User

class GetUsers(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(), username=graphene.String())

    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_user(self, info, id=None, username=None):
        query = User.query
        if id:
            return query.filter(User.id == id).first()
        if username:
            return query.filter(User.username == username).first()
        return None