from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, SenInfo, db
from .return_types import ReturnType
from utils.dbUtils import adddb, commitdb, rollbackdb

class SeniorType(SQLAlchemyObjectType):
    class Meta:
        model = SenInfo



class SeniorsQuery(graphene.ObjectType):
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
        gender = graphene.String()
        dob = graphene.DateTime()
        address = graphene.String()
        pincode = graphene.String()
        alternate_phone_num = graphene.String()
        medical_info = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, ez_id, gender, dob, address, pincode, alternate_phone_num, medical_info=None):
        user = User.query.get(ez_id)
        if not user:
            return ReturnType(message="User not found", status=404)
        if user.role != 0:
            return ReturnType(message="User is not a senior citizen", status=403)
        
        if SenInfo.query.filter_by(ez_id=ez_id).first():
            return ReturnType(message="Senior citizen already exists", status=403)
        
        senior = SenInfo(ez_id=ez_id, gender=gender, dob=dob, address=address, pincode=pincode, alternate_phone_num=alternate_phone_num, medical_info=medical_info)

        adddb(senior)
        try:
            commitdb()
            return ReturnType(message="Senior added successfully", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error adding senior: {e}")
            return ReturnType(message=f"Something went wrong", status=500)



class UpdateSenior(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        address = graphene.String()
        pincode = graphene.String()
        alternate_phone_num = graphene.String()
        medical_info = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, sen_id, address, pincode, alternate_phone_num, medical_info=None):
        senior = SenInfo.query.get(sen_id)
        if not senior:
            return ReturnType(message="Senior not found", status=0)
        if medical_info is not None:
            senior.medical_info = medical_info
        if address is not None:
            senior.address = address
        if pincode is not None:
            senior.pincode = pincode
        if alternate_phone_num is not None:
            senior.alternate_phone_num = alternate_phone_num

        try: 
            commitdb()
            return ReturnType(message="Senior updated successfully", status=1)
        except Exception as e:
            rollbackdb()
            print(f"Error updating senior: {e}")
            return ReturnType(message="Something went wrong", status=500)
        

class SeniorsMutation(graphene.ObjectType):
    add_senior = AddSenior.Field()
    update_senior = UpdateSenior.Field()