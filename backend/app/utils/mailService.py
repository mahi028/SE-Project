from flask_mail import Mail, Message
from datetime import datetime
from flask import render_template
from typing import List
import logging

logger = logging.getLogger(__name__)
mail = Mail()

def send_email(subject: str, contact: object, recipients: List[str], reminder_display) -> None:
    """Send an elegant email reminder using Flask-Mail."""
    try:
        msg = Message(
            subject=f"⏰ Reminder: {contact.label}",
            recipients=recipients,
        )

        current_year = datetime.now().year

        # You can expand or change this template to include rich formatting, inline styling, etc.
        msg.html = render_template(
            'email_template.html',
            reminder=reminder_display,
            current_year=current_year
        )

        msg.body = f"This is a reminder for: {contact.label}. Check your dashboard for more details."

        mail.send(msg)
        logger.info(f"Email sent to {recipients} for reminder: {contact.label}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise RuntimeError("Failed to send email") from e