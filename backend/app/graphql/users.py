from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, db
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from .return_types import ReturnType
from ..utils.authControl import get_user

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
        exclude_fields = ('password',)

        

class UsersQuery(graphene.ObjectType):
    all_users = graphene.List(UserType)
    get_me = graphene.Field(UserType)
    get_user = graphene.Field(UserType, ez_id = graphene.String(required=True))

    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_get_me(self, info):
        return get_user(info)
    
    def resolve_get_user(self, info, ez_id):
        user = User.query.get(ez_id)
        if user:
            return User.query.get(ez_id)
        return ReturnType(status=404, message="User Not Found")


class UsersMutation(graphene.ObjectType):
    pass