from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, db
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from .return_types import ReturnType
from ..utils.authControl import get_user

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
        

class UsersQuery(graphene.ObjectType):
    all_users = graphene.List(UserType)
    get_user = graphene.Field(UserType)

    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_get_user(self, info):
        return get_user(info)


class UsersMutation(graphene.ObjectType):
    pass