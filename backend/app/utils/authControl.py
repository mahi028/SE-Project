from functools import wraps
from flask_jwt_extended import jwt_required, current_user
from flask import request, abort
from ..models import User, SenInfo, DocInfo  # ✅ Added missing imports


def get_user(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    user = User.query.get(ez_id)
    return user


def get_senior(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    
    # First validate the user and role
    user = User.query.get(ez_id)
    if not user:
        raise Exception("User not found")
    if user.role != 0:
        raise Exception("UnAuthorised Access! Senior Only.")
    
    # Get and return the SenInfo profile
    senior = SenInfo.query.filter_by(ez_id=ez_id).first()
    if not senior:  # ✅ Fixed: was 'senior_profile'
        raise Exception("Senior Profile Not Complete!.")
    
    return senior


def get_doctor(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    
    # First validate the user and role
    user = User.query.get(ez_id)
    if not user:
        raise Exception("User not found")
    if user.role != 1:
        raise Exception("UnAuthorised Access! Doctors Only.")
    
    # Get and return the DocInfo profile
    doctor = DocInfo.query.filter_by(ez_id=ez_id).first()
    if not doctor:  # ✅ Fixed: was 'doctor_profile'
        raise Exception("Doctor Profile Not Complete!.")
    
    return doctor


def get_mod(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    mod = User.query.get(ez_id)
    if mod.role != 2:
        raise Exception("UnAuthorised Access! Moderators Only.")
    return mod
