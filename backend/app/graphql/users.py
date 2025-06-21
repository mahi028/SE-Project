from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, db
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from .return_types import ReturnType

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
        

class GetUsers(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(), email=graphene.String())

    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_user(self, info, id=None, email=None):
        if id:
            return User.query.filter(User.id == id).first()
        if email:
            return User.query.filter(User.email == email).first()
        return None


class AddUser(graphene.Mutation):
    class Arguments:
        ez_id = graphene.String(required=True)  # Optional field for easy identification
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        gender = graphene.String(required=True)
        age = graphene.Int(required=True)
        phone_num = graphene.String(required=True)
        alternate_phone_num = graphene.String()
        pincode = graphene.String(required=True)
        profile_image_url = graphene.String() # TBD

    Output = ReturnType

    def mutate(root, info, ez_id, email, password, name, gender, age, phone_num, pincode, profile_image_url, alternate_phone_num=None):
        try:
            new_user = User(
                ez_id=ez_id,
                email=email, password=password, name=name, phone_num=phone_num, pincode=pincode, profile_image_url=profile_image_url, alternate_phone_num=alternate_phone_num
            )

            adddb(new_user)
            commitdb()
        except Exception as err:
            rollbackdb()
            print(err)
            return ReturnType(message="Failure", status=500)
        else:
            return ReturnType(message="Success, User created successfully", status=201)
        

#Dev Gupta's Code to Akhil