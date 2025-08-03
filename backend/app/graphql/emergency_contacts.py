from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import EmergencyContacts, db, SenInfo
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from ..utils.authControl import get_senior

class EmergencyContactType(SQLAlchemyObjectType):
    class Meta:
        model = EmergencyContacts

# Query for getting emergency contacts by senior citizen ID
class EmergencyContactsQuery(graphene.ObjectType):
    get_emergency_contacts = graphene.List(EmergencyContactType, sen_id=graphene.Int(required=True))

    def resolve_get_emergency_contacts(self, info):
        senior = get_senior(info)
        return EmergencyContacts.query.filter_by(sen_id=senior.sen_id).all()

# Mutation for adding an emergency contact
class AddEmergencyContact(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone_num = graphene.String(required=True)
        send_alert = graphene.Boolean(required=True)
        relationship = graphene.String(required=True)

    Output = ReturnType

    def mutate(self, info, name, email, phone_num, send_alert, relationship):
        senior = get_senior(info)

        contact = EmergencyContacts(
            sen_id=senior.sen_id,
            name=name,
            email=email,
            phone_num=phone_num,
            send_alert=send_alert,
            relationship=relationship
        )
        adddb(contact)
        try:
            commitdb()    
            return ReturnType(message="Emergency contact added successfully", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error adding emergency contact: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=500)
        

# Mutation for updating an emergency contact
class UpdateEmergencyContact(graphene.Mutation):
    class Arguments:
        cont_id = graphene.Int(required=True)
        name = graphene.String()
        email = graphene.String()
        phone_num = graphene.String()
        send_alert = graphene.Boolean()
        relationship = graphene.String()

    Output = ReturnType

    def mutate(self, info, cont_id, name=None, email=None, phone_num=None, send_alert=None, relationship=None):
        senior = get_senior(info)
        contact = EmergencyContacts.query.filter_by(cont_id=cont_id).first()
        if not contact:
            return ReturnType(message="Contact not found", status=0)
        if contact.sen_info.sen_id != senior.sen_id:
            return ReturnType(message="UnAuthorized", status=401)

        if name is not None:
            contact.name = name
        if email is not None:
            contact.email = email
        if phone_num is not None:
            contact.phone_num = phone_num
        if send_alert is not None:
            contact.send_alert = send_alert
        if relationship is not None:
            contact.relationship = relationship
        try:
            commitdb()
            return ReturnType(message="Emergency contact updated successfully", status=200)
        except Exception as e:
            rollbackdb()
            print(f"Error updating emergency contact: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=403)
        

class EmergencyContactMutation(graphene.ObjectType):
    add_emergency_contact = AddEmergencyContact.Field()
    update_emergency_contact = UpdateEmergencyContact.Field()