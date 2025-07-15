from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, SenInfo, db
from .return_types import ReturnType

class SeniorType(SQLAlchemyObjectType):
    class Meta:
        model = SenInfo



class Query(graphene.ObjectType):
    get_seniors = graphene.List(SeniorType)
    get_senior = graphene.List(SeniorType, sen_id=graphene.Int(required=True))
    
    def resolve_get_seniors(self, info,):
        return SenInfo.query.all()


    def resolve_get_doctor(self, info, sen_id):
        return SenInfo.query.get(sen_id)



# Mutations for adding/updating seniors

class AddSenior(graphene.Mutation):
    class Arguments:
        ez_id = graphene.String(required=True)
        medical_info = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, ez_id, medical_info=None):
        # Check if user exists
        user = User.query.filter_by(ez_id=ez_id).first()
        if not user:
            return ReturnType(message="User not found", status=0)
        senior = SenInfo(ez_id=ez_id, medical_info=medical_info)
        db.session.add(senior)
        db.session.commit()
        return ReturnType(message="Senior added successfully", status=1)

class UpdateSenior(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        medical_info = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, sen_id, medical_info=None):
        senior = SenInfo.query.filter_by(sen_id=sen_id).first()
        if not senior:
            return ReturnType(message="Senior not found", status=0)
        if medical_info is not None:
            senior.medical_info = medical_info
        db.session.commit()
        return ReturnType(message="Senior updated successfully", status=1)

class Mutation(graphene.ObjectType):
    add_senior = AddSenior.Field()
    update_senior = UpdateSenior.Field()