from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Appointments, db
from .return_types import ReturnType

class AppointmentType(SQLAlchemyObjectType):
    class Meta:
        model = Appointments

# Query for getting appointments by senior citizen ID or doctor ID
class Query(graphene.ObjectType):
    get_appointments_for_senior = graphene.List(AppointmentType, sen_id=graphene.Int(required=True))
    get_appointments_for_doctor = graphene.List(AppointmentType, doc_id=graphene.Int(required=True))

    def resolve_get_appointments_for_senior(self, info, sen_id):
        return Appointments.query.filter_by(sen_id=sen_id).all()

    def resolve_get_appointments_for_doctor(self, info, doc_id):
        return Appointments.query.filter_by(doc_id=doc_id).all()

# Mutation for booking an appointment (by senior citizen)
class BookAppointment(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        doc_id = graphene.Int(required=True)
        rem_time = graphene.DateTime(required=True)
        reason = graphene.String(required=True)

    Output = ReturnType

    def mutate(self, info, sen_id, doc_id, rem_time, reason):
        appointment = Appointments(
            sen_id=sen_id,
            doc_id=doc_id,
            rem_time=rem_time,
            reason=reason,
            status=0  # pending by default
        )
        db.session.add(appointment)
        db.session.commit()
        return ReturnType(message="Appointment booked successfully", status=1)

# Mutation for updating appointment status (accept/reject by doctor)
class UpdateAppointmentStatus(graphene.Mutation):
    class Arguments:
        app_id = graphene.Int(required=True)
        status = graphene.Int(required=True)  # 1=confirmed, -1=rejected

    Output = ReturnType

    def mutate(self, info, app_id, status):
        appointment = Appointments.query.filter_by(app_id=app_id).first()
        if not appointment:
            return ReturnType(message="Appointment not found", status=0)
        if status not in [1, -1]:
            return ReturnType(message="Invalid status", status=0)
        appointment.status = status
        db.session.commit()
        return ReturnType(message="Appointment status updated", status=1)

class Mutation(graphene.ObjectType):
    book_appointment = BookAppointment.Field()
    update_appointment_status = UpdateAppointmentStatus.Field()