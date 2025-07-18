from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Group, Joinee, db, Reminders, SenInfo
from .return_types import ReturnType
from datetime import timedelta

class GroupType(SQLAlchemyObjectType):
    class Meta:
        model = Group

class JoineeType(SQLAlchemyObjectType):
    class Meta:
        model = Joinee

# Queries: fetch all groups, groups by admin, and members of a group
class PeerGroupQuery(graphene.ObjectType):
    get_groups = graphene.List(
        GroupType,
        admin=graphene.Int(),
        pincode=graphene.String()
    )
    get_group_members = graphene.List(JoineeType, grp_id=graphene.Int(required=True))

    def resolve_get_groups(self, info, admin=None, pincode=None):
        query = Group.query
        if admin is not None:
            query = query.filter_by(admin=admin)
        if pincode is not None:
            query = query.filter_by(pincode=pincode)
        return query.all()

    def resolve_get_group_members(self, info, grp_id):
        return Joinee.query.filter_by(grp_id=grp_id).all()

# Mutation: create group (by senior), join group (by senior)
class CreateGroup(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        timing = graphene.DateTime(required=True)
        admin = graphene.Int(required=True)
        pincode = graphene.String()
        location = graphene.String()

    Output = ReturnType

    def mutate(self, info, label, timing, admin, pincode=None, location=None):
        group = Group(
            label=label,
            timing=timing,
            admin=admin,
            pincode=pincode,
            location=location
        )
        db.session.add(group)
        db.session.commit()
        return ReturnType(message="Group created successfully", status=1)

class JoinGroup(graphene.Mutation):
    class Arguments:
        grp_id = graphene.Int(required=True)
        sen_id = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, grp_id, sen_id):
        group = Group.query.get(grp_id)
        if not group:
            return ReturnType(message="Group not found", status=404)
            
        existing = Joinee.query.filter_by(grp_id=grp_id, sen_id=sen_id).first()
        if existing:
            return ReturnType(message="Already joined", status=0)

        # Get senior's ez_id for reminder
        senior = SenInfo.query.get(sen_id)
        if not senior:
            return ReturnType(message="Senior not found", status=404)

        joinee = Joinee(grp_id=grp_id, sen_id=sen_id)
        db.session.add(joinee)

        # Create reminder 1 hour before group timing
        hour_before = group.timing - timedelta(hours=1)
        reminder = Reminders(
            ez_id=senior.ez_id,
            label=f"Group Meeting: {group.label}",
            category=3,  # group meeting category
            rem_time=hour_before,
            is_active=True,
            is_recurring=False,
            frequency=None,
            interval=1,
            weekdays=None,
            times_per_day=1,
            time_slots=None
        )
        db.session.add(reminder)

        try:
            db.session.commit()
            return ReturnType(message="Joined group successfully and reminder set", status=1)
        except Exception as e:
            db.session.rollback()
            return ReturnType(message=f"Error joining group: {str(e)}", status=403)

class Mutation(graphene.ObjectType):
    create_group = CreateGroup.Field()
    join_group = JoinGroup.Field()
