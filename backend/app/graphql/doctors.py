from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User,DocInfo, db
from .return_types import ReturnType
from utils.dbUtils import adddb, commitdb, rollbackdb

class DoctorType(SQLAlchemyObjectType):
    class Meta:
        model = DocInfo



class DoctorsQuery(graphene.ObjectType):
    get_doctors = graphene.List(DoctorType, pin=graphene.String(required=False),specialization=graphene.String(required=False))
    get_doctor = graphene.Field(DoctorType, doc_id=graphene.Int(required=True))
    

    def resolve_get_doctors(self, info, pin=None, specialization=None):
        query = DocInfo.query
        if pin:
            query=DocInfo.query.filter_by(pin=pin)
        if specialization:
            query=DocInfo.query.filter_by(specialization=specialization)
        return query.all()


    def resolve_get_doctor(self, info, doc_id):
        return DocInfo.query.get(doc_id)



# Example Mutations for adding/updating doctors (expand as needed)
class AddDoctor(graphene.Mutation):
    class Arguments:
        ez_id = graphene.String(required=True)
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

    def mutate(self, info, ez_id, license_number, **kwargs):
        # Check if doctor with same license number exists
        user = User.query.get(ez_id)
        if not user:
            return ReturnType(message="User not found", status=404)
        if user.role != 1:
            return ReturnType(message="User is not a health professional", status=403)
        
        if DocInfo.query.filter_by(ez_id=ez_id).first():
            return ReturnType(message="Doctor already exists", status=0)
        if DocInfo.query.filter_by(license_number=license_number).first():
            return ReturnType(message="Doctor with this license number already exists", status=0)

        doctor = DocInfo(ez_id=ez_id, license_number=license_number, **kwargs)
        adddb(doctor)
        try:
            commitdb()
            return ReturnType(message="Doctor added successfully", status=1)
        except Exception as e:
            rollbackdb()
            print(f"Error adding doctor: {e}")
            return ReturnType(message=f"Something fcuking happened:", status=0)


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
        doctor = DocInfo.query.filter_by(doc_id=doc_id).first()
        if not doctor:
            return ReturnType(message="Health Professional not found", status=0)

        # If updating license number, check if it conflicts with another doctor
        if 'license_number' in kwargs:
            existing_doctor = DocInfo.query.filter(
                DocInfo.license_number == kwargs['license_number'],
                DocInfo.doc_id != doc_id
            ).first()
            if existing_doctor:
                return ReturnType(message="License number already exists", status=0)

        for key, value in kwargs.items():
            if value is not None:
                setattr(doctor, key, value)

        try:
            commitdb()
            return ReturnType(message="Doctor updated successfully", status=1)
        except Exception as e:
            rollbackdb()
            return ReturnType(message=f"Error updating doctor: {str(e)}", status=0)

class DoctorMutation(graphene.ObjectType):
    add_doctor = AddDoctor.Field()
    update_doctor = UpdateDoctor.Field()
