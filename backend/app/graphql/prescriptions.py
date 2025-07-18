from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Prescription, Reminders, SenInfo, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from datetime import datetime, time

class PrescriptionType(SQLAlchemyObjectType):
    class Meta:
        model = Prescription

class PrescriptionsQuery(graphene.ObjectType):
    get_prescription = graphene.Field(PrescriptionType, pres_id=graphene.Int(required=True))
    get_prescriptions_for_senior = graphene.List(PrescriptionType, sen_id=graphene.Int(required=True))
    get_prescriptions_for_doctor = graphene.List(PrescriptionType, doc_id=graphene.Int(required=True))
    get_all_prescriptions = graphene.List(PrescriptionType)

    def resolve_get_prescription(self, info, pres_id):
        return Prescription.query.get(pres_id)

    def resolve_get_prescriptions_for_senior(self, info, sen_id):
        return Prescription.query.filter_by(sen_id=sen_id).all()

    def resolve_get_prescriptions_for_doctor(self, info, doc_id):
        return Prescription.query.filter_by(doc_id=doc_id).all()
    
    def resolve_get_all_prescriptions(self, info):
        return Prescription.query.all()

class AddPrescription(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        doc_id = graphene.Int(required=False)  # Optional for self-added prescriptions
        medication_data = graphene.String(required=True)
        time = graphene.JSONString(required=True)
        instructions = graphene.String(required=True)

    Output = ReturnType

    def mutate(self, info, sen_id, medication_data, time, instructions, doc_id=None):
        # Get senior's ez_id for reminders
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
        # time format example: {"morning": "08:00", "afternoon": "14:00", "evening": "20:00"}
        try:
            # Extract time slots from the time JSON
            time_slots = [time_str for time_str in time.values()]
            
            # Create a single recurring reminder for all medication times
            reminder = Reminders(
                ez_id=senior.ez_id,
                label=f"Medicine: {medication_data}",
                category=1,  # medication category
                rem_time=datetime.combine(datetime.now().date(), datetime.strptime(time_slots[0], "%H:%M").time()),
                is_active=True,
                is_recurring=True,
                frequency='daily',
                interval=1,
                weekdays=None,  # Daily means all days
                times_per_day=len(time_slots),
                time_slots=time_slots
            )
            adddb(reminder)

            commitdb(db)
            return ReturnType(message="Prescription and reminders added successfully", status=201)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error adding prescription: {str(e)}", status=403)

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
            return ReturnType(message="Prescription not found", status=404)
        
        if medication_data is not None:
            prescription.medication_data = medication_data
        if time is not None:
            prescription.time = time
        if instructions is not None:
            prescription.instructions = instructions
            
        try:
            commitdb(db)
            return ReturnType(message="Prescription updated successfully", status=200)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error updating prescription: {str(e)}", status=403)

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
            commitdb(db)
            return ReturnType(message="Prescription deleted successfully", status=200)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error deleting prescription: {str(e)}", status=403)

class PrescriptionsMutation(graphene.ObjectType):
    add_prescription = AddPrescription.Field()
    update_prescription = UpdatePrescription.Field()
    delete_prescription = DeletePrescription.Field()
