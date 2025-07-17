from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Appointments, db
from .return_types import ReturnType

class AppointmentType(SQLAlchemyObjectType):
    class Meta:
        model = Appointments


class AppointmentsQuery(graphene.ObjectType):
    get_appointments_for_senior = graphene.List(AppointmentType, sen_id=graphene.Int(required=True))
    get_appointments_for_doctor = graphene.List(AppointmentType, doc_id=graphene.Int(required=True))
    get_appointments_for_doctor_senior = graphene.List(AppointmentType, sen_id=graphene.Int(required=True), doc_id=graphene.Int(required=True))
    get_appointment_data = graphene.List(AppointmentType)
    get_available_slots = graphene.List(
        graphene.String,
        doc_id=graphene.Int(required=True),
        date=graphene.String(required=True)
    )


    def resolve_get_appointments_for_senior(self, info, sen_id):
        return Appointments.query.filter_by(sen_id=sen_id).all()

    def resolve_get_appointments_for_doctor(self, info, doc_id):
        return Appointments.query.filter_by(doc_id=doc_id).all()
    
    def resolve_get_appointments_for_doctor_senior(self, info, sen_id, doc_id):
        return Appointments.query.filter_by(sen_id=sen_id, doc_id=doc_id).all()
    
    def resolve_get_available_slots(self, info, doc_id, date):
        # Example: 9am-5pm every hour
        slots = [f"{hour:02d}:00 AM" if hour < 12 else f"{hour-12 or 12:02d}:00 PM" for hour in range(9, 18)]
        appointments = Appointments.query.filter(
            Appointments.doc_id == doc_id,
            db.func.date(Appointments.rem_time) == date,
            Appointments.status != -1
        ).all()
        booked_times = {apt.rem_time.strftime('%I:%M %p') for apt in appointments}
        return [slot for slot in slots if slot not in booked_times]

    

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


class CancelAppointment(graphene.Mutation):
        class Arguments:
            app_id = graphene.Int(required=True)

        Output = ReturnType

        def mutate(self, info, app_id):
            appointment = Appointments.query.filter_by(app_id=app_id).first()
            if not appointment:
                return ReturnType(message="Appointment not found", status=0)
            appointment.status = -1  # Mark as cancelled
            db.session.commit()
            return ReturnType(message="Appointment cancelled successfully", status=1)


class AppointmentsMutation(graphene.ObjectType):
    book_appointment = BookAppointment.Field()
    update_appointment_status = UpdateAppointmentStatus.Field()
    cancel_appointment = CancelAppointment.Field()

    
