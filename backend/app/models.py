from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Roles(Enum):
    SEN = '10'
    DOC = '01'
    MOD = '11'

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]


class User(db.Model):
    __tablename__ = 'users'
    ez_id = db.Column(db.String(32), primary_key=True)  # format: ez(role)(10auto_num)name
    role = db.Column(db.Enum(Roles), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(8))
    age = db.Column(db.Integer)
    phone_num = db.Column(db.String(10), unique=True, nullable=False)
    alternate_phone_num = db.Column(db.String(10))
    pincode = db.Column(db.String(6))
    # more_address_field = db.Column(db.String(256))  # tbd
    profile_image_url = db.Column(db.String(256))
    
    # Relationships
    sen_info = db.relationship('SenInfo', backref='user', uselist=False)
    doc_info = db.relationship('DocInfo', backref='user', uselist=False)
    reminders = db.relationship('Reminders', backref='user', lazy=True)



class SenInfo(db.Model):
    __tablename__ = 'sen_info'
    sen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)
    medical_info = db.Column(db.JSON)
    
    # Relationships
    embeddings = db.relationship('Embeddings', backref='sen_info', lazy=True)
    emergency_contacts = db.relationship('EmergencyContacts', backref='sen_info', lazy=True)
    vital_logs = db.relationship('VitalLogs', backref='sen_info', lazy=True)
    appointments = db.relationship('Appointments', backref='sen_info', lazy=True)
    doc_reviews = db.relationship('DocReviews', backref='sen_info', lazy=True)
    groups_admin = db.relationship('Group', backref='admin_sen', foreign_keys='Group.admin', lazy=True)


class Embeddings(db.Model):
    __tablename__ = 'embeddings'
    emb_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    vector = db.Column(db.PickleType)


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
    specialization = db.Column(db.String(128))
    qualification = db.Column(db.String(128))
    experience = db.Column(db.String(32))
    hospital = db.Column(db.String(128))
    address = db.Column(db.String(256))
    consultation_fee = db.Column(db.Float, default=0.0)
    working_hours = db.Column(db.String(64))  # e.g., "10:00 AM - 6:00 PM"
    availability = db.Column(db.JSON)         # e.g., ["Monday", "Tuesday", ...]
    reviews = db.Column(db.Integer)           # average rating or review count
    availability_status = db.Column(db.Integer, default=1)  # 1=active, 0=pending, -1=rejected
    documents = db.Column(db.JSON)            # {id_proof, medical_license, qualification_cert, passport_photo}
    appointment_window = db.Column(db.Integer, default=30)  # in minutes

    # Relationships
    doc_reviews = db.relationship('DocReviews', backref='doc_info', lazy=True)
    appointments = db.relationship('Appointments', backref='doc_info', lazy=True)


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
    category = db.Column(db.Integer)  # [medic, hyd, group, ...]
    rem_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)



class Appointments(db.Model):
    __tablename__ = 'appointments'
    app_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_info.doc_id'))
    rem_time = db.Column(db.DateTime)
    reason = db.Column(db.String(256))
    status = db.Column(db.Integer, default=0)  # 0=pending, 1=confirmed, -1=canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VitalTypes(db.Model):
    __tablename__ = 'vital_types'
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(64), unique=True)
    unit = db.Column(db.String(32))  # e.g., "mmHg", "bpm", "mg/dL"
    threshold = db.Column(db.JSON)  # threshold value for alerting
    

class VitalLogs(db.Model):
    __tablename__ = 'vital_logs'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    vital_type_id = db.Column(db.Integer, db.ForeignKey('vital_types.type_id'))
    reading= db.Column(db.String(64))  # e.g., "120/80 mmHg"
    logged_at = db.Column(db.DateTime)



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
