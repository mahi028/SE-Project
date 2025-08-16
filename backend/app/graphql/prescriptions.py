from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Prescription, Reminders, SenInfo, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from datetime import datetime, time, timedelta
from ..utils.authControl import get_senior, get_doctor

class PrescriptionType(SQLAlchemyObjectType):
    class Meta:
        model = Prescription

class PrescriptionsQuery(graphene.ObjectType):
    get_prescription = graphene.Field(PrescriptionType, pres_id=graphene.Int(required=True))
    get_prescriptions_for_senior = graphene.List(PrescriptionType)
    get_prescriptions_for_doctor = graphene.List(PrescriptionType)
    get_all_prescriptions = graphene.List(PrescriptionType)

    def resolve_get_prescription(self, info, pres_id):
        return Prescription.query.get(pres_id)

    def resolve_get_prescriptions_for_senior(self, info):
        senior = get_senior(info)
        return Prescription.query.filter_by(sen_id=senior.sen_id).all()

    def resolve_get_prescriptions_for_doctor(self, info):
        doctor = get_doctor(info)
        return Prescription.query.filter_by(doc_id=doctor.doc_id).all()
    
    def resolve_get_all_prescriptions(self, info):
        return Prescription.query.all()

class AddPrescription(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=False)  # Optional - will use current user if not provided
        doc_id = graphene.Int(required=False)  # Optional for self-added prescriptions
        medication_data = graphene.String(required=True)
        time = graphene.JSONString(required=True)
        instructions = graphene.String(required=True)

    Output = ReturnType

    def mutate(self, info, medication_data, time, instructions, sen_id=None, doc_id=None):
        # If sen_id not provided, use current user (for self-added prescriptions)
        if sen_id is None:
            senior = get_senior(info)
            if not senior:
                return ReturnType(message="Senior not found", status=404)
            sen_id = senior.sen_id
        else:
            senior = SenInfo.query.get(sen_id)
            if not senior:
                return ReturnType(message="Senior not found", status=404)

        prescription = Prescription(
            sen_id=sen_id,
            doc_id=doc_id,
            medication_data=medication_data,
            time=time,
            instructions=instructions
        )
        adddb(prescription)

        # Create reminders for each time specified in the prescription
        try:
            # time format example: {"times": ["08:00", "14:00", "20:00"], "frequency": "Daily"}
            time_data = time if isinstance(time, dict) else {"times": [time], "frequency": "Daily"}
            time_slots = time_data.get("times", [])
            frequency = time_data.get("frequency", "Daily")
            
            if time_slots:
                # Create a recurring reminder for the medication
                first_time = datetime.strptime(time_slots[0], "%H:%M").time()
                next_reminder = datetime.combine(datetime.now().date(), first_time)
                
                # If the time has passed today, schedule for tomorrow
                if next_reminder <= datetime.now():
                    next_reminder = datetime.combine(
                        datetime.now().date() + timedelta(days=1), 
                        first_time
                    )

                reminder = Reminders(
                    ez_id=senior.ez_id,
                    label=f"Medicine: {medication_data}",
                    category=1,  # medication category
                    rem_time=next_reminder,
                    is_active=True,
                    is_recurring=True,
                    frequency=frequency.lower(),
                    interval=1,
                    weekdays=None if frequency.lower() == 'daily' else frequency,
                    times_per_day=len(time_slots),
                    time_slots=time_slots
                )
                adddb(reminder)

            commitdb()
            return ReturnType(message="Medicine schedule added successfully", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error adding prescription: {str(e)}")
            return ReturnType(message=f"Error adding medicine schedule", status=403)

class UpdatePrescription(graphene.Mutation):
    class Arguments:
        pres_id = graphene.Int(required=True)
        medication_data = graphene.String(required=False)
        time = graphene.JSONString(required=False)
        instructions = graphene.String(required=False)

    Output = ReturnType

    def mutate(self, info, pres_id, medication_data=None, time=None, instructions=None):
        prescription = Prescription.query.get(pres_id)
        if not prescription:
            return ReturnType(message="Medicine schedule not found", status=404)
        
        # Check authorization - only the senior or their doctor can update
        current_senior = get_senior(info)
        if current_senior and current_senior.sen_id != prescription.sen_id:
            return ReturnType(message="Unauthorized", status=403)
        
        if medication_data is not None:
            prescription.medication_data = medication_data
        if time is not None:
            prescription.time = time
        if instructions is not None:
            prescription.instructions = instructions
            
        try:
            # Update related reminders if time or medication changed
            if time is not None or medication_data is not None:
                # Find and update related reminders
                old_reminders = Reminders.query.filter(
                    Reminders.ez_id == prescription.sen_info.ez_id,
                    Reminders.label.like(f"%{prescription.medication_data}%"),
                    Reminders.category == 1
                ).all()
                
                # Delete old reminders
                for reminder in old_reminders:
                    deletedb(reminder)
                
                # Create new reminders if time was updated
                if time is not None:
                    time_data = time if isinstance(time, dict) else {"times": [time], "frequency": "Daily"}
                    time_slots = time_data.get("times", [])
                    frequency = time_data.get("frequency", "Daily")
                    
                    if time_slots:
                        first_time = datetime.strptime(time_slots[0], "%H:%M").time()
                        next_reminder = datetime.combine(datetime.now().date(), first_time)
                        
                        if next_reminder <= datetime.now():
                            next_reminder = datetime.combine(
                                datetime.now().date() + timedelta(days=1), 
                                first_time
                            )

                        new_reminder = Reminders(
                            ez_id=prescription.sen_info.ez_id,
                            label=f"Medicine: {medication_data or prescription.medication_data}",
                            category=1,
                            rem_time=next_reminder,
                            is_active=True,
                            is_recurring=True,
                            frequency=frequency.lower(),
                            interval=1,
                            weekdays=None if frequency.lower() == 'daily' else frequency,
                            times_per_day=len(time_slots),
                            time_slots=time_slots
                        )
                        adddb(new_reminder)
            
            commitdb()
            return ReturnType(message="Medicine schedule updated successfully", status=200)
        except Exception as e:
            rollbackdb()
            print(f"Error updating prescription: {str(e)}")
            return ReturnType(message=f"Error updating medicine schedule", status=403)

class DeletePrescription(graphene.Mutation):
    class Arguments:
        pres_id = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, pres_id):
        prescription = Prescription.query.get(pres_id)
        if not prescription:
            return ReturnType(message="Prescription not found", status=404)
        
        try:
            deletedb(prescription)
            commitdb()
            return ReturnType(message="Prescription deleted successfully", status=200)
        except Exception as e:
            rollbackdb()
            return ReturnType(message=f"Error deleting prescription: {str(e)}", status=403)

class PrescriptionsMutation(graphene.ObjectType):
    add_prescription = AddPrescription.Field()
    update_prescription = UpdatePrescription.Field()
    delete_prescription = DeletePrescription.Field()
