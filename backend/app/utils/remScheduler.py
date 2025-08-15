from datetime import datetime, timedelta, time
from dateutil.rrule import rrule, WEEKLY
from flask_apscheduler import APScheduler
from ..models import Reminders, Notification
from .dbUtils import commitdb, rollbackdb, adddb
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
    subject = f"⏰ Reminder: {reminder.label}"

    # Access user email via relationship
    if not reminder.user or not reminder.user.email:
        print(f"Missing user or email for reminder {reminder.rem_id}")
        return

    recipients = [reminder.user.email]
    reminder_display = {
        'label': reminder.label,
        'category': CATEGORY_MAP.get(reminder.category, "Other"),
        'rem_time': reminder.rem_time.strftime('%Y-%m-%d %H:%M:%S') if reminder.rem_time else None,
        'is_recurring': reminder.is_recurring,
        'frequency': reminder.frequency,
        'weekdays': reminder.weekdays,
        'times_per_day': reminder.times_per_day,
        'time_slots': reminder.time_slots,
        'interval': reminder.interval,
        'is_active': reminder.is_active
    }
    try:
        send_email(
            subject=subject,
            recipients=recipients,
            reminder_display=reminder_display,
            template="reminders_template.html",
            current_year=datetime.now().year
        )
        # Create notification using the actual reminder object attributes, not the dictionary
        notification = Notification(
            ez_id=reminder.user.ez_id,
            label=reminder.label,
            time=reminder.rem_time,
            category=reminder.category
        )
        adddb(notification)
        commitdb()
        print(f"Email sent for Reminder: {reminder.label} to {reminder.user.email}")
    except Exception as e:
        rollbackdb()
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
                app.logger.error(f"Error triggering one-time reminder ID {rem.rem_id}: {e}")
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
                app.logger.error(f"Error triggering recurring reminder ID {rem.rem_id}: {e}")
                rollbackdb()
