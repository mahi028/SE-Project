from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, DocInfo, DocReviews, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from ..utils.authControl import get_user, get_doctor, get_mod

class DoctorType(SQLAlchemyObjectType):
    class Meta:
        model = DocInfo

class DoctorsQuery(graphene.ObjectType):
    get_doctors = graphene.List(
        DoctorType,
        pincode=graphene.String(required=False),
        specialization=graphene.String(required=False),
        status=graphene.Int(required=False),
        include_all_status=graphene.Boolean(required=False)
    )
    get_all_doctors = graphene.List(DoctorType)
    get_doctor = graphene.Field(DoctorType)
    get_approved_doctors = graphene.List(DoctorType, pincode=graphene.String(required=False))

    def resolve_get_doctors(self, info, pincode=None, specialization=None, status=None, include_all_status=False):
        query = DocInfo.query.join(User)

        # Handle status filtering
        if status is not None:
            # If specific status is requested, filter by that status
            query = query.filter(DocInfo.availability_status == status)
        elif not include_all_status:
            # If no specific status and not including all, default to approved only
            query = query.filter(DocInfo.availability_status == 1)
        # If include_all_status is True and status is None, don't filter by status

        # Apply other filters
        if pincode:
            query = query.filter(DocInfo.pincode == pincode)
        if specialization:
            query = query.filter(DocInfo.specialization.ilike(f'%{specialization}%'))

        return query.all()

    def resolve_get_all_doctors(self, info):
        # For moderators - get all doctors regardless of status
        return DocInfo.query.join(User).all()

    def resolve_get_approved_doctors(self, info, pincode=None):
        # For regular users - only approved doctors
        query = DocInfo.query.join(User).filter(DocInfo.availability_status == 1)
        if pincode:
            query = query.filter(DocInfo.pincode == pincode)
        return query.all()

    def resolve_get_doctor(self, info):
        return get_doctor(info)



# Example Mutations for adding/updating doctors (expand as needed)
class AddDoctor(graphene.Mutation):
    class Arguments:
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

class UpdateDoctorStatus(graphene.Mutation):
    class Arguments:
        ez_id = graphene.String(required=True)
        availability_status = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, ez_id, availability_status):
        # Authenticate moderator
        mod = get_mod(info)
        if not mod:
            return ReturnType(message="Unauthorized access. Moderators only.", status=403)

        # Validate status value
        if availability_status not in [1, 0, -1, -2]:
            return ReturnType(message="Invalid status. Must be 1 (approved), 0 (pending), -1 (rejected), or -2 (flagged)", status=400)

        # Find the doctor by ez_id
        doctor = DocInfo.query.filter_by(ez_id=ez_id).first()
        if not doctor:
            return ReturnType(message="Doctor not found", status=404)

        # Update the status
        old_status = doctor.availability_status
        doctor.availability_status = availability_status

        try:
            commitdb()

            # Create status labels for logging
            status_labels = {
                1: "approved",
                0: "pending",
                -1: "rejected",
                -2: "flagged"
            }

            old_label = status_labels.get(old_status, "unknown")
            new_label = status_labels.get(availability_status, "unknown")

            return ReturnType(
                message=f"Doctor status updated from {old_label} to {new_label} successfully",
                status=200
            )
        except Exception as e:
            rollbackdb()
            print(f"Error updating doctor status: {e}")
            return ReturnType(message=f"Error updating doctor status: {str(e)}", status=500)

class DoctorMutation(graphene.ObjectType):
    add_doctor = AddDoctor.Field()
    update_doctor = UpdateDoctor.Field()
    update_doctor_status = UpdateDoctorStatus.Field()
