from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User,DocInfo, db
from .return_types import ReturnType

class DoctorType(SQLAlchemyObjectType):
    class Meta:
        model = DocInfo



class Query(graphene.ObjectType):
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
        specialization = graphene.String()
        qualification = graphene.String()
        experience = graphene.String()
        hospital = graphene.String()
        address = graphene.String()
        consultation_fee = graphene.Float()
        working_hours = graphene.String()
        availability = graphene.JSONString()
        documents = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, ez_id, **kwargs):
        doctor = DocInfo(ez_id=ez_id, **kwargs)
        db.session.add(doctor)
        db.session.commit()
        return ReturnType(message="Doctor added successfully", status=1)

class UpdateDoctor(graphene.Mutation):
    class Arguments:
        doc_id = graphene.Int(required=True)
        specialization = graphene.String()
        qualification = graphene.String()
        experience = graphene.String()
        hospital = graphene.String()
        address = graphene.String()
        consultation_fee = graphene.Float()
        working_hours = graphene.String()
        availability = graphene.JSONString()
        documents = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, doc_id, **kwargs):
        doctor = DocInfo.query.filter_by(doc_id=doc_id).first()
        if not doctor:
            return ReturnType(message="Doctor not found", status=0)
        for key, value in kwargs.items():
            if value is not None:
                setattr(doctor, key, value)
        db.session.commit()
        return ReturnType(message="Doctor updated successfully", status=1)

class Mutation(graphene.ObjectType):
    add_doctor = AddDoctor.Field()
    update_doctor = UpdateDoctor.Field()
