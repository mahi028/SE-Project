from datetime import datetime, timedelta, time
from dateutil.rrule import rrule, WEEKLY
from flask_apscheduler import APScheduler
from ..models import Reminders 
from .dbUtils import commitdb, rollbackdb
from .mailService import send_email

scheduler = APScheduler()
CATEGORY_MAP = {
    0: 'Appointments',
    1: 'Medic',
    2: 'Hydration',
    3: 'Group',
    4: 'Exercise',
    5: 'Diet',
    6: 'Sleep',
    # Add more if needed
}

def should_trigger_today(reminder: Reminders, now: datetime) -> bool:
    """Check if reminder should be triggered today based on weekdays."""
    if not reminder.weekdays:
        return True  # No restriction, always trigger

    today_str = now.strftime('%a').lower()[:3]  # mon, tue, ...
    return today_str in [d.strip().lower() for d in reminder.weekdays.split(',')]

def should_trigger_now(reminder: Reminders, now: datetime) -> bool:
    """Check if current time matches any time slot ± 1 min"""
    if not reminder.time_slots:
        return abs((reminder.rem_time - now).total_seconds()) < 60

    for slot in reminder.time_slots:
        slot_time = datetime.combine(now.date(), time.fromisoformat(slot))
        if abs((slot_time - now).total_seconds()) < 60:
            return True
    return False

def trigger_reminder(reminder: Reminders):
    """Trigger reminder and send email."""
    subject = f"Reminder: {reminder.label}"
    contact = reminder

    # Access user email via relationship
    if not reminder.user or not reminder.user.email:
        print(f"Missing user or email for reminder {reminder.rem_id}")
        return

    recipients = [reminder.user.email]
    reminder_display = {
        **reminder.__dict__,
        "category": CATEGORY_MAP.get(reminder.category, "Other")  # fallback to "Other"
    }
    try:
        send_email(subject, contact, recipients, reminder_display)
        print(f"Email sent for Reminder: {reminder.label} to {reminder.user.email}")
    except Exception as e:
        print(f"Error sending email for {reminder.label}: {e}")

def check_reminders(app):
    with app.app_context():
        now = datetime.utcnow()

        # --- One-time reminders ---
        one_time_reminders = Reminders.query.filter(
            Reminders.is_active == True,
            Reminders.is_recurring == False,
            Reminders.rem_time <= now
        ).all()

        for rem in one_time_reminders:
            try:
                trigger_reminder(rem)
                rem.is_active = False
                commitdb()
            except Exception as e:
                app.logger.error(f"Error triggering one-time reminder ID {rem.id}: {e}")
                rollbackdb()

        # --- Recurring reminders ---
        recurring_reminders = Reminders.query.filter(
            Reminders.is_active == True,
            Reminders.is_recurring == True
        ).all()

        for rem in recurring_reminders:
            try:
                if should_trigger_today(rem, now) and should_trigger_now(rem, now):
                    trigger_reminder(rem)
                    # Optional: update rem.last_triggered = now
                    commitdb()
            except Exception as e:
                app.logger.error(f"Error triggering recurring reminder ID {rem.id}: {e}")
                rollbackdb()
