from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Appointments, Reminders, db, SenInfo, DocInfo, User
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from datetime import timedelta
from ..utils.authControl import get_doctor, get_senior, get_user


class AppointmentType(SQLAlchemyObjectType):
    class Meta:
        model = Appointments


class AvailableSlotsType(graphene.ObjectType):
    slots = graphene.List(graphene.String)


class AppointmentsQuery(graphene.ObjectType):
    get_appointments_for_senior = graphene.List(AppointmentType)
    get_appointments_for_doctor = graphene.List(AppointmentType)
    get_appointments_for_doctor_senior = graphene.List(AppointmentType, sen_id=graphene.String(required=True), doc_id=graphene.String(required=True))
    get_available_slots = graphene.Field(
        AvailableSlotsType,
        doc_id=graphene.Int(required=True),
        date=graphene.String(required=True)
    )

    def resolve_get_appointments_for_senior(self, info):
        senior = get_senior(info)
        return Appointments.query.filter_by(sen_id=senior.sen_id).all()

    def resolve_get_appointments_for_doctor(self, info):
        doctor = get_doctor(info)
        return Appointments.query.filter_by(doc_id=doctor.doc_id).all()

    def resolve_get_appointments_for_doctor_senior(self, info, sen_id, doc_id):
        senior = User.query.get(sen_id)
        doctor = User.query.get(doc_id)
        if (senior and senior.sen_info) and (doctor and doctor.doc_info):
            return Appointments.query.filter_by(sen_id=senior.sen_info.sen_id, doc_id=doctor.doc_info.doc_id).all()

    def resolve_get_available_slots(self, info, doc_id, date):
        # Get doctor information
        doctor = DocInfo.query.get(doc_id)
        if not doctor:
            return AvailableSlotsType(slots=[])

        # Parse the date string (format: DD-MM-YYYY)
        try:
            from datetime import datetime
            date_parts = date.split('-')
            if len(date_parts) != 3:
                return AvailableSlotsType(slots=[])

            day, month, year = map(int, date_parts)
            target_date = datetime(year, month, day)
            day_name = target_date.strftime('%A')  # Get day name like 'Wednesday'
        except (ValueError, IndexError):
            return AvailableSlotsType(slots=[])

        # Check if doctor is available on this day
        availability = doctor.availability
        if availability:
            try:
                # Handle JSON string or already parsed list
                if isinstance(availability, str):
                    import json
                    available_days = json.loads(availability)
                else:
                    available_days = availability

                if day_name not in available_days:
                    return AvailableSlotsType(slots=[])  # Doctor not available on this day
            except (json.JSONDecodeError, TypeError):
                return AvailableSlotsType(slots=[])
        else:
            return AvailableSlotsType(slots=[])

        # Parse working hours
        working_hours = doctor.working_hours
        if not working_hours:
            return AvailableSlotsType(slots=[])

        try:
            # Parse "08:30 - 15:30" format
            start_time_str, end_time_str = working_hours.split(' - ')
            start_hour, start_minute = map(int, start_time_str.split(':'))
            end_hour, end_minute = map(int, end_time_str.split(':'))
        except (ValueError, AttributeError):
            # Fallback to default hours if parsing fails
            start_hour, start_minute = 9, 0
            end_hour, end_minute = 17, 0

        # Get appointment window (default 30 minutes)
        appointment_window = doctor.appointment_window or 30

        # Generate time slots based on working hours and appointment window
        slots = []
        current_hour = start_hour
        current_minute = start_minute

        while (current_hour < end_hour) or (current_hour == end_hour and current_minute < end_minute):
            # Format time slot
            if current_hour == 0:
                time_str = f"12:{current_minute:02d} AM"
            elif current_hour < 12:
                time_str = f"{current_hour:02d}:{current_minute:02d} AM"
            elif current_hour == 12:
                time_str = f"12:{current_minute:02d} PM"
            else:
                time_str = f"{current_hour-12:02d}:{current_minute:02d} PM"

            slots.append(time_str)

            # Increment by appointment window
            current_minute += appointment_window
            if current_minute >= 60:
                current_hour += current_minute // 60
                current_minute = current_minute % 60

        # Filter out already booked slots
        appointments = Appointments.query.filter(
            Appointments.doc_id == doc_id,
            db.func.date(Appointments.rem_time) == target_date.date(),
            Appointments.status != -1  # Exclude cancelled appointments
        ).all()

        booked_times = set()
        for apt in appointments:
            booked_time = apt.rem_time.strftime('%I:%M %p').lstrip('0')
            # Handle cases where strftime might return '01:00 PM' vs '1:00 PM'
            booked_times.add(booked_time)
            # Also add version with leading zero for consistency
            booked_times.add(apt.rem_time.strftime('%I:%M %p'))

        available_slots = []
        for slot in slots:
            # Check both formats for consistency
            slot_no_leading_zero = slot.lstrip('0')
            if slot not in booked_times and slot_no_leading_zero not in booked_times:
                available_slots.append(slot)

        return AvailableSlotsType(slots=available_slots)


class BookAppointment(graphene.Mutation):
    class Arguments:
        doc_id = graphene.Int(required=True)
        rem_time = graphene.DateTime(required=True)
        reason = graphene.String(required=True)

    Output = ReturnType

    def mutate(self, info, doc_id, rem_time, reason):
        senior = get_senior(info)
        doctor = DocInfo.query.get(doc_id)

        appointment = Appointments(
            sen_id=senior.sen_id,
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
        doctor = get_doctor(info)

        appointment = Appointments.query.get(app_id)
        if not appointment:
            return ReturnType(message="Appointment not found", status=0)
        if appointment.doc_info.doc_id != doctor.doc_id:
            return ReturnType(message="UnAuthorised", status=401)
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

        user = get_user(info)

        appointment = Appointments.query.get(app_id)

        if not appointment:
            return ReturnType(message="Appointment not found", status=0)
        if appointment.sen_info.ez_id != user.ez_id and appointment.doc_info.ez_id != user.ez_id:
            return ReturnType(message="UnAuthorised", status=401)
        try:
            appointment.status = -1  # Mark as cancelled
            commitdb()
            return ReturnType(message="Appointment cancelled successfully", status=1)
        except Exception as e:
            rollbackdb()
            return ReturnType(message=f"Error updating appointment status", status=403)


class AppointmentsMutation(graphene.ObjectType):
    book_appointment = BookAppointment.Field()
    update_appointment_status = UpdateAppointmentStatus.Field()
    cancel_appointment = CancelAppointment.Field()
