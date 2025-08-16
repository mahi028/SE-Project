import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..models import VitalLogs, SenInfo, EmergencyContacts, User, db
from datetime import datetime
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from ..utils.authControl import get_senior
from ..utils.vital_types_data import get_vital_type_by_id
from ..utils.mailService import send_email
from .vital_types import VitalTypeType  # Import instead of redefining
import logging

logger = logging.getLogger(__name__)

class VitalLogType(SQLAlchemyObjectType):
    class Meta:
        model = VitalLogs
    
    # Add the vitalType field that the frontend expects
    vital_type = graphene.Field(VitalTypeType)
    
    def resolve_vital_type(self, info):
        # Get vital type data from hardcoded data
        vital_type_data = get_vital_type_by_id(self.vital_type_id)
        if vital_type_data:
            return VitalTypeType(
                type_id=vital_type_data['type_id'],
                label=vital_type_data['label'],
                unit=vital_type_data['unit'],
                threshold=vital_type_data['threshold']
            )
        return None

class VitalLogsQuery(graphene.ObjectType):
    get_vital_logs = graphene.List(
        VitalLogType,
        sen_id=graphene.Int(required=True),
        vital_type_id=graphene.Int(required=False)
    )
    get_vital_logs_by_senior = graphene.List(VitalLogType)  # Add this query for current senior
    get_vital_log = graphene.Field(VitalLogType, log_id=graphene.Int(required=True))

    def resolve_get_vital_logs(self, info, sen_id, vital_type_id=None):
        query = VitalLogs.query.filter_by(sen_id=sen_id)
        if vital_type_id:
            query = query.filter_by(vital_type_id=vital_type_id)
        return query.order_by(VitalLogs.logged_at.desc()).all()

    def resolve_get_vital_logs_by_senior(self, info):
        # Get current senior from authentication
        senior = get_senior(info)
        if not senior:
            return []
        return VitalLogs.query.filter_by(sen_id=senior.sen_id).order_by(VitalLogs.logged_at.desc()).all()

    def resolve_get_vital_log(self, info, log_id):
        return VitalLogs.query.get(log_id)

def check_threshold(vital_type_data, reading):
    """Check if the vital reading is outside the threshold."""
    threshold = vital_type_data.get('threshold')
    if not threshold:
        return False  # No threshold defined
    
    try:
        # Handle different vital types
        if vital_type_data['label'] == 'Blood Pressure':
            return check_blood_pressure_threshold(threshold, reading)
        else:
            return check_numeric_threshold(threshold, reading)
    except Exception as e:
        logger.error(f"Error checking threshold for {vital_type_data['label']}: {str(e)}")
        return False

def check_blood_pressure_threshold(threshold, reading):
    """Check blood pressure threshold (format: '120/80')."""
    try:
        if '/' not in reading:
            return False
        
        systolic_str, diastolic_str = reading.split('/')
        systolic = float(systolic_str.strip())
        diastolic = float(diastolic_str.strip())
        
        systolic_threshold = threshold.get('systolic', {})
        diastolic_threshold = threshold.get('diastolic', {})
        
        # Check systolic
        systolic_low = systolic_threshold.get('low')
        systolic_high = systolic_threshold.get('high')
        
        # Check diastolic
        diastolic_low = diastolic_threshold.get('low')
        diastolic_high = diastolic_threshold.get('high')
        
        is_outside = False
        
        if systolic_low and systolic < systolic_low:
            is_outside = True
        if systolic_high and systolic > systolic_high:
            is_outside = True
        if diastolic_low and diastolic < diastolic_low:
            is_outside = True
        if diastolic_high and diastolic > diastolic_high:
            is_outside = True
            
        return is_outside
        
    except (ValueError, AttributeError) as e:
        logger.error(f"Error parsing blood pressure reading '{reading}': {str(e)}")
        return False

def check_numeric_threshold(threshold, reading):
    """Check numeric threshold for other vital types."""
    try:
        # Extract numeric value from reading (remove units)
        numeric_value = float(''.join(filter(lambda x: x.isdigit() or x == '.', reading)))
        
        low_threshold = threshold.get('low')
        high_threshold = threshold.get('high')
        
        is_outside = False
        
        if low_threshold and numeric_value < low_threshold:
            is_outside = True
        if high_threshold and numeric_value > high_threshold:
            is_outside = True
            
        return is_outside
        
    except (ValueError, AttributeError) as e:
        logger.error(f"Error parsing numeric reading '{reading}': {str(e)}")
        return False

def send_threshold_alert_emails(senior, vital_type_data, reading, logged_at):
    """Send email alerts to emergency contacts."""
    try:
        # Get senior's user info
        senior_user = User.query.filter_by(ez_id=senior.ez_id).first()
        if not senior_user:
            logger.error(f"User not found for senior {senior.sen_id}")
            return
        
        # Get emergency contacts with email alerts enabled
        emergency_contacts = EmergencyContacts.query.filter_by(
            sen_id=senior.sen_id,
            send_alert=True
        ).all()
        
        if not emergency_contacts:
            logger.info(f"No emergency contacts with email alerts for senior {senior.sen_id}")
            return
        
        # Prepare email data
        alert_data = {
            'senior_name': senior_user.name,
            'senior_ezid': senior.ez_id,
            'vital_type': vital_type_data['label'],
            'reading': reading,
            'unit': vital_type_data['unit'],
            'threshold': vital_type_data['threshold'],
            'logged_at': logged_at.strftime('%Y-%m-%d %H:%M:%S'),
            'alert_type': 'vital_threshold'
        }
        
        # Get recipient emails
        recipient_emails = [contact.email for contact in emergency_contacts if contact.email]
        
        if recipient_emails:
            subject = f"EZCare Alert: {vital_type_data['label']} Reading Outside Normal Range"
            
            # Send email using the existing mail service
            send_email(
                subject=subject,
                recipients=recipient_emails,
                reminder_display=alert_data,
                template="vital_alert_template.html"
            )
            
            logger.info(f"Vital threshold alert sent to {len(recipient_emails)} contacts for senior {senior.sen_id}")
        else:
            logger.warning(f"No valid email addresses found in emergency contacts for senior {senior.sen_id}")
            
    except Exception as e:
        logger.error(f"Error sending threshold alert emails: {str(e)}")

class AddVitalLog(graphene.Mutation):
    class Arguments:
        vital_type_id = graphene.Int(required=True)
        reading = graphene.String(required=True)
        logged_at = graphene.DateTime(required=False)
        sen_id = graphene.Int(required=False)  # Optional - will use current user if not provided

    Output = ReturnType

    def mutate(self, info, vital_type_id, reading, logged_at=None, sen_id=None):
        # If sen_id not provided, use current user
        if sen_id is None:
            senior = get_senior(info)
            if not senior:
                return ReturnType(message="Senior not found", status=404)
            sen_id = senior.sen_id
        else:
            senior = SenInfo.query.get(sen_id)
            if not senior:
                return ReturnType(message="Senior not found", status=404)

        # Verify vital type exists in hardcoded data
        vital_type_data = get_vital_type_by_id(vital_type_id)
        if not vital_type_data:
            return ReturnType(message="Vital type not found", status=404)

        # Use current time if not provided
        if logged_at is None:
            logged_at = datetime.now()

        vital_log = VitalLogs(
            sen_id=sen_id,
            vital_type_id=vital_type_id,
            reading=reading,
            logged_at=logged_at
        )
        adddb(vital_log)

        try:
            commitdb()
            
            # Check if vital reading is outside threshold
            is_outside_threshold = check_threshold(vital_type_data, reading)
            
            if is_outside_threshold:
                # Send email to emergency contacts
                send_threshold_alert_emails(senior, vital_type_data, reading, logged_at)
            
            return ReturnType(message="Vital log added successfully", status=201)
        except Exception as e:
            rollbackdb()
            logger.error(f"Error adding vital log: {str(e)}")
            return ReturnType(message="Error adding vital log", status=500)
class VitalLogsMutation(graphene.ObjectType):
    add_vital_log = AddVitalLog.Field()