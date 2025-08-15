from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, Notification
from .return_types import ReturnType
from ..utils.authControl import get_user

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
        exclude_fields = ('password',)

class NotificationType(SQLAlchemyObjectType):
    class Meta:
        model = Notification

class UsersQuery(graphene.ObjectType):
    all_users = graphene.List(UserType)
    get_me = graphene.Field(UserType)
    get_user = graphene.Field(UserType, ez_id = graphene.String(required=True))
    get_user_by_email = graphene.Field(UserType, email = graphene.String(required=True))
    get_user_notifications = graphene.List(NotificationType)  # Changed from Field to List

    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_get_me(self, info):
        return get_user(info)
    
    def resolve_get_user(self, info, ez_id):
        user = User.query.get(ez_id)
        if user:
            return user
        return ReturnType(status=404, message="User Not Found")
    
    def resolve_get_user_by_email(self, info, email):
        user = User.query.filter_by(email=email).one_or_none()
        if user:
            return user
        return ReturnType(status=404, message="User Not Found")
    
    def resolve_get_user_notifications(self, info):
        user = get_user(info)
        if user:
            notifications = Notification.query.filter_by(ez_id=user.ez_id).all()
            return notifications
        return []  # Return empty list instead of ReturnType for better error handling


class UsersMutation(graphene.ObjectType):
    pass