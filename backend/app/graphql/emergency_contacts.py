from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import EmergencyContacts, db
from .return_types import ReturnType

class EmergencyContactType(SQLAlchemyObjectType):
    class Meta:
        model = EmergencyContacts

# Query for getting emergency contacts by senior citizen ID
class Query(graphene.ObjectType):
    get_emergency_contacts = graphene.List(EmergencyContactType, sen_id=graphene.Int(required=True))

    def resolve_get_emergency_contacts(self, info, sen_id):
        return EmergencyContacts.query.filter_by(sen_id=sen_id).all()

# Mutation for adding an emergency contact
class AddEmergencyContact(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        email = graphene.String()
        phone_num = graphene.String()
        send_alert = graphene.Boolean()
        relationship = graphene.String()

    Output = ReturnType

    def mutate(self, info, sen_id, name, email=None, phone_num=None, send_alert=False, relationship=None):
        contact = EmergencyContacts(
            sen_id=sen_id,
            name=name,
            email=email,
            phone_num=phone_num,
            send_alert=send_alert,
            relationship=relationship
        )
        db.session.add(contact)
        db.session.commit()
        return ReturnType(message="Emergency contact added successfully", status=1)

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
        contact = EmergencyContacts.query.filter_by(cont_id=cont_id).first()
        if not contact:
            return ReturnType(message="Contact not found", status=0)
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
        db.session.commit()
        return ReturnType(message="Emergency contact updated successfully", status=1)

class Mutation(graphene.ObjectType):
    add_emergency_contact = AddEmergencyContact.Field()
    update_emergency_contact = UpdateEmergencyContact.Field()