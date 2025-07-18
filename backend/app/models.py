from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Roles(Enum):
    SEN = '0'
    DOC = '1'
    MOD = '2'

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]


class User(db.Model):
    __tablename__ = 'users'
    ez_id = db.Column(db.String(32), primary_key=True)  # format: ez(role)(10auto_num)name
    role = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    phone_num = db.Column(db.String(10), unique=True, nullable=False)
    profile_image_url = db.Column(db.String(256))
    
    # Relationships
    sen_info = db.relationship('SenInfo', backref='user', uselist=False)
    doc_info = db.relationship('DocInfo', backref='user', uselist=False)
    reminders = db.relationship('Reminders', backref='user', lazy=True)



class SenInfo(db.Model):
    __tablename__ = 'sen_info'
    sen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)
    gender = db.Column(db.String(8))
    dob = db.Column(db.DateTime)
    address = db.Column(db.Text)
    pincode = db.Column(db.String(6))
    alternate_phone_num = db.Column(db.String(10))
    medical_info = db.Column(db.JSON)
    
    # Relationships
    embeddings = db.relationship('Embeddings', backref='sen_info', lazy=True)
    emergency_contacts = db.relationship('EmergencyContacts', backref='sen_info', lazy=True)
    vital_logs = db.relationship('VitalLogs', backref='sen_info', lazy=True)
    appointments = db.relationship('Appointments', backref='sen_info', lazy=True)
    doc_reviews = db.relationship('DocReviews', backref='sen_info', lazy=True)
    groups_admin = db.relationship('Group', backref='admin_sen', foreign_keys='Group.admin', lazy=True)
    prescriptions = db.relationship('Prescription', backref='sen_info', lazy=True)



class EmergencyContacts(db.Model):
    __tablename__ = 'emergency_contacts'
    cont_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone_num = db.Column(db.String(10))
    send_alert = db.Column(db.Boolean, default=False)
    relationship = db.Column(db.String(64))
    


class DocInfo(db.Model):
    __tablename__ = 'doc_info'
    doc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)
    gender = db.Column(db.String(8))
    dob = db.Column(db.DateTime)
    address = db.Column(db.Text)
    pincode = db.Column(db.String(6))
    alternate_phone_num = db.Column(db.String(10))
    license_number = db.Column(db.String(64), unique=True, nullable=False)
    specialization = db.Column(db.String(128))
    affiliation = db.Column(db.JSON) 
    qualification = db.Column(db.JSON)
    experience = db.Column(db.Integer, default=0)  # in years
    consultation_fee = db.Column(db.Float, default=0.0)
    working_hours = db.Column(db.String(64))  
    availability = db.Column(db.JSON)         
    reviews = db.Column(db.Integer)          
    availability_status = db.Column(db.Integer, default=1)  # 1=active, 0=pending, -1=rejected
    documents = db.Column(db.JSON)
    appointment_window = db.Column(db.Integer, default=30)  # in minutes

    # Relationships
    doc_reviews = db.relationship('DocReviews', backref='doc_info', lazy=True)
    appointments = db.relationship('Appointments', backref='doc_info', lazy=True)
    prescriptions = db.relationship('Prescription', backref='doc_info', lazy=True)


class DocReviews(db.Model):
    __tablename__ = 'doc_reviews'
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_info.doc_id'))
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)



class Reminders(db.Model):
    __tablename__ = 'reminders'
    
    rem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)

    label = db.Column(db.String(128))
    category = db.Column(db.Integer)  # [appointments:0, medic:1, hydration:2, group:3, ...]
    rem_time = db.Column(db.DateTime)  # First or next occurrence time
    is_active = db.Column(db.Boolean, default=True)
    
    is_recurring = db.Column(db.Boolean, default=False)
    frequency = db.Column(db.String(32))  # 'daily', 'weekly', 'monthly', etc.
    interval = db.Column(db.Integer, default=1)  # e.g., every 2 days
    weekdays = db.Column(db.String(64))  # comma-separated days: 'mon,tue,thu'
    times_per_day = db.Column(db.Integer, default=1)  # for multiple reminders/day
    time_slots = db.Column(db.JSON)  # optional: store ['08:00', '20:00']



class Appointments(db.Model):
    __tablename__ = 'appointments'
    app_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_info.doc_id'))
    rem_time = db.Column(db.DateTime)
    reason = db.Column(db.String(256))
    status = db.Column(db.Integer, default=0)  # 0=pending, 1=confirmed, -1=canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    pres_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_info.doc_id'), nullable=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    medication_data = db.Column(db.String(64))  
    time=db.Column(db.JSON)
    instructions = db.Column(db.String(256)) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VitalTypes(db.Model):
    __tablename__ = 'vital_types'
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(64), unique=True)
    unit = db.Column(db.String(32))  # e.g., "mmHg", "bpm", "mg/dL"
    threshold = db.Column(db.JSON)  # threshold value for alerting
    vital_logs = db.relationship('VitalLogs', backref='vital_type', lazy=True)
    

class VitalLogs(db.Model):
    __tablename__ = 'vital_logs'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    vital_type_id = db.Column(db.Integer, db.ForeignKey('vital_types.type_id'))
    reading= db.Column(db.String(64))  # e.g., "120/80 mmHg"
    logged_at = db.Column(db.DateTime)
    vital_type = db.relationship('VitalTypes', backref='vital_logs', lazy=True)


class Group(db.Model):
    __tablename__ = 'groups'
    grp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(128))
    timing = db.Column(db.DateTime)
    admin = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    pincode = db.Column(db.String(6)) 
    location = db.Column(db.String(256))
    #relationships
    joinee=db.relationship('Joinee', backref='group', lazy=True)


class Joinee(db.Model):
    __tablename__ = 'joinee'
    grp_id = db.Column(db.Integer, db.ForeignKey('groups.grp_id'), primary_key=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
