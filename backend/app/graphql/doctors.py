from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User,DocInfo, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from ..utils.authControl import get_user, get_doctor

class DoctorType(SQLAlchemyObjectType):
    class Meta:
        model = DocInfo



class DoctorsQuery(graphene.ObjectType):
    get_doctors = graphene.List(DoctorType, pincode=graphene.String(required=False),specialization=graphene.String(required=False))
    get_doctor = graphene.Field(DoctorType)
    

    def resolve_get_doctors(self, info, pincode=None, specialization=None):
        query = DocInfo.query
        if pincode:
            query=DocInfo.query.filter_by(pincode=pincode)
        if specialization:
            query=DocInfo.query.filter_by(specialization=specialization)
        return query.all()


    def resolve_get_doctor(self, info):
        return get_doctor(info)



# Example Mutations for adding/updating doctors (expand as needed)
class AddDoctor(graphene.Mutation):
    class Arguments:
        # ez_id = graphene.String(required=True)
        gender = graphene.String()
        dob = graphene.DateTime()
        address = graphene.String()
        pincode = graphene.String()
        alternate_phone_num = graphene.String()
        license_number = graphene.String(required=True)
        specialization = graphene.String()
        affiliation = graphene.JSONString()
        qualification = graphene.JSONString()
        experience = graphene.Int()
        consultation_fee = graphene.Float()
        working_hours = graphene.String()
        availability = graphene.JSONString()
        documents = graphene.JSONString()
        appointment_window = graphene.Int()

    Output = ReturnType

    def mutate(self, info, license_number, **kwargs):
        # Check if doctor with same license number exists
        user = get_user(info)
        if not user:
            return ReturnType(message="User not found", status=404)
        if user.role != 1:
            return ReturnType(message="User is not a health professional", status=403)
        
        if DocInfo.query.filter_by(ez_id=user.ez_id).one_or_none():
            return ReturnType(message="Doctor already exists", status=0)
        if DocInfo.query.filter_by(license_number=license_number).one_or_none():
            return ReturnType(message="Doctor with this license number already exists", status=0)

        doctor = DocInfo(ez_id=user.ez_id, license_number=license_number, **kwargs)
        adddb(doctor)
        try:
            commitdb()
            return ReturnType(message="Doctor added successfully", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error adding doctor: {e}")
            return ReturnType(message=f"Something fcuking happened:", status=403)


class UpdateDoctor(graphene.Mutation):
    class Arguments:
        doc_id = graphene.Int(required=True)
        address = graphene.String()
        pincode = graphene.String()
        alternate_phone_num = graphene.String()
        affiliation = graphene.JSONString()
        experience = graphene.Int()
        consultation_fee = graphene.Float()
        working_hours = graphene.String()
        availability = graphene.JSONString()
        documents = graphene.JSONString()
        availability_status = graphene.Int()
        appointment_window = graphene.Int()

    Output = ReturnType

    def mutate(self, info, doc_id, **kwargs):
        doctor = get_doctor(info)
        if not doctor:
            return ReturnType(message="Health Professional not found", status=403)

        # If updating license number, check if it conflicts with another doctor
        if 'license_number' in kwargs:
            existing_doctor = DocInfo.query.filter(
                DocInfo.license_number == kwargs['license_number'],
                DocInfo.doc_id != doc_id
            ).first()
            if existing_doctor:
                return ReturnType(message="License number already exists", status=403)

        for key, value in kwargs.items():
            if value is not None:
                setattr(doctor, key, value)

        try:
            commitdb()
            return ReturnType(message="Doctor updated successfully", status=200)
        except Exception as e:
            rollbackdb()
            return ReturnType(message=f"Error updating doctor: {str(e)}", status=403)

class DoctorMutation(graphene.ObjectType):
    add_doctor = AddDoctor.Field()
    update_doctor = UpdateDoctor.Field()
