from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, db
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from .return_types import ReturnType

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
        

class UsersQuery(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, ez_id=graphene.Int(), email=graphene.String())

    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_user(self, info, ez_id=None, email=None):
        if ez_id:
            return User.query.get(ez_id)
        if email:
            return User.query.filter(User.email == email).one_or_none()
        return None


class AddUser(graphene.Mutation):
    class Arguments:
        ez_id = graphene.String(required=True)  # Optional field for easy identification
        role = graphene.String(required=True)  # Optional field for user role
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        gender = graphene.String(required=True)
        age = graphene.Int(required=True)
        phone_num = graphene.String(required=True)
        profile_image_url = graphene.String() # TBD

    Output = ReturnType

    def mutate(root, info, ez_id, role, email, password, name, gender, age, phone_num, profile_image_url):
        try:
            new_user = User(
                ez_id=ez_id, role=role,
                email=email, password=password, name=name, phone_num=phone_num, profile_image_url=profile_image_url
                )

            adddb(new_user)
            commitdb()
        except Exception as err:
            rollbackdb()
            print(err)
            return ReturnType(message="Failure", status=500)
        else:
            return ReturnType(message="Success, User created successfully", status=201)


class UsersMutation(graphene.ObjectType):
    add_user = AddUser.Field()