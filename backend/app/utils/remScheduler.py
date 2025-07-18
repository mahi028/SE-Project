from datetime import datetime, timedelta, time
from dateutil.rrule import rrule, WEEKLY
from flask_apscheduler import APScheduler
from ..models import Reminders  # replace with your actual import
from.dbUtils import commitdb

scheduler = APScheduler()

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
    # Your actual logic (send email, push, DB log, etc.)
    print(f"Triggering Reminder: {reminder.label} (User {reminder.ez_id})")

def check_reminders():
    now = datetime.utcnow()

    # --- One-time reminders ---
    one_time_reminders = Reminders.query.filter(
        Reminders.is_active == True,
        Reminders.is_recurring == False,
        Reminders.rem_time <= now
    ).all()

    for rem in one_time_reminders:
        trigger_reminder(rem)
        rem.is_active = False
        commitdb()

    # --- Recurring reminders ---
    recurring_reminders = Reminders.query.filter(
        Reminders.is_active == True,
        Reminders.is_recurring == True
    ).all()

    for rem in recurring_reminders:
        if should_trigger_today(rem, now) and should_trigger_now(rem, now):
            trigger_reminder(rem)
            # Optional: track last_triggered if needed
