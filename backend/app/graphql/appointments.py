from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Appointments, Reminders, db, SenInfo, DocInfo
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from datetime import timedelta


class AppointmentType(SQLAlchemyObjectType):
    class Meta:
        model = Appointments


class AvailableSlotsType(graphene.ObjectType):
    slots = graphene.List(graphene.String)


class AppointmentsQuery(graphene.ObjectType):
    get_appointments_for_senior = graphene.List(AppointmentType, sen_id=graphene.Int(required=True))
    get_appointments_for_doctor = graphene.List(AppointmentType, doc_id=graphene.Int(required=True))
    get_appointments_for_doctor_senior = graphene.List(AppointmentType, sen_id=graphene.Int(required=True), doc_id=graphene.Int(required=True))
    get_appointment_data = graphene.List(AppointmentType)
    get_available_slots = graphene.Field(
        AvailableSlotsType,
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
        available_slots = [slot for slot in slots if slot not in booked_times]
        return AvailableSlotsType(slots=available_slots)


class BookAppointment(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        doc_id = graphene.Int(required=True)
        rem_time = graphene.DateTime(required=True)
        reason = graphene.String(required=True)

    Output = ReturnType

    def mutate(self, info, sen_id, doc_id, rem_time, reason):
        senior = SenInfo.query.get(sen_id)
        doctor = DocInfo.query.get(doc_id)

        if not senior:
            pass

        if not doctor:
            pass

        appointment = Appointments(
            sen_id=sen_id,
            doc_id=doc_id,
            rem_time=rem_time,
            reason=reason,
            status=0  # pending by default
        )
        adddb(appointment)

        # Create reminder for 1 day before
        day_before = rem_time - timedelta(days=1)
        reminder_day = Reminders(
            ez_id=senior.ez_id,
            label=f"Appointment with Dr. {doctor.user.name}",
            category=0,  # appointment category
            rem_time=day_before,
            is_active=True,
            is_recurring=False,
            frequency=None,
            interval=1,
            weekdays=None,
            times_per_day=1,
            time_slots=None
        )
        adddb(reminder_day)

        # Create reminder for 1 hour before
        hour_before = rem_time - timedelta(hours=1)
        reminder_hour = Reminders(
            ez_id=senior.ez_id,
            label=f"Appointment with Dr. {doctor.user.name}",
            category=0,
            rem_time=hour_before,
            is_active=True,
            is_recurring=False,
            frequency=None,
            interval=1,
            weekdays=None,
            times_per_day=1,
            time_slots=None
        )
        adddb(reminder_hour)

        try:    
            commitdb()
            return ReturnType(message="Appointment booked successfully with reminders", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error booking appointment: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=403)


class UpdateAppointmentStatus(graphene.Mutation):
    class Arguments:
        app_id = graphene.Int(required=True)
        status = graphene.Int(required=True)  # 1=confirmed, -1=rejected

    Output = ReturnType

    def mutate(self, info, app_id, status):
        appointment = Appointments.query.get(app_id)
        if not appointment:
            return ReturnType(message="Appointment not found", status=0)
        if status not in [1, -1]:
            return ReturnType(message="Invalid status", status=0)
        appointment.status = status
        try:
            commitdb()
            return ReturnType(message="Appointment status updated", status=200)
        except Exception as e:
            rollbackdb()
            return ReturnType(message=f"Error updating appointment status", status=403)


class CancelAppointment(graphene.Mutation):
    class Arguments:
        app_id = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, app_id):
        appointment = Appointments.query.get(app_id)
        if not appointment:
            return ReturnType(message="Appointment not found", status=0)
        appointment.status = -1  # Mark as cancelled
        commitdb()
        return ReturnType(message="Appointment cancelled successfully", status=1)


class AppointmentsMutation(graphene.ObjectType):
    book_appointment = BookAppointment.Field()
    update_appointment_status = UpdateAppointmentStatus.Field()
    cancel_appointment = CancelAppointment.Field()

#Dev
#IncreaseCommits
#FightForTopSpot
