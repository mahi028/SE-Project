from flask_mail import Mail, Message
from datetime import datetime
from flask import render_template
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
mail = Mail()

def send_email(subject: str, recipients: List[str], reminder_display=None, template="reminders_template.html", contact=None, current_year=None) -> None:
    """Send an email using Flask-Mail.
    
    Args:
        subject: Email subject line
        recipients: List of recipient email addresses
        reminder_display: Dictionary containing reminder/SOS data for template rendering
        template: Template file name to use
        contact: Contact object for backward compatibility with reminder emails
        current_year: Current year for template rendering
    """
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
        )

        # Set current_year if not provided
        if current_year is None:
            current_year = datetime.now().year

        # Handle different template rendering scenarios
        if template == "SOS_template.html":
            # SOS email rendering
            msg.html = render_template(
                template,
                reminder_display=reminder_display,
                current_year=current_year
            )
            
            # SOS plain text fallback
            senior_name = "Senior Citizen"
            if reminder_display and 'ezId' in reminder_display:
                senior_name = f"Senior Citizen (ID: {reminder_display['ezId']})"
            
            msg.body = f"EMERGENCY SOS ALERT: {senior_name} needs urgent help! Please check the email for full details and contact information."
            
        else:
            # Regular reminder email rendering
            template_vars = {
                'current_year': current_year
            }
            
            # Handle reminder data safely
            if reminder_display:
                template_vars['reminder'] = reminder_display
            
            # Handle contact object for backward compatibility
            if contact:
                template_vars['contact'] = contact
                
            try:
                msg.html = render_template(template, **template_vars)
                
                # Create plain text fallback
                if contact and hasattr(contact, 'label'):
                    msg.body = f"This is a reminder for: {contact.label}. Check your dashboard for more details."
                elif reminder_display and 'label' in reminder_display:
                    msg.body = f"This is a reminder for: {reminder_display['label']}. Check your dashboard for more details."
                else:
                    msg.body = "You have a new reminder. Please check your email for details."
                    
            except Exception as template_error:
                logger.error(f"Template rendering failed: {template_error}")
                # Fallback to simple HTML
                reminder_label = (
                    contact.label if contact and hasattr(contact, 'label') else
                    reminder_display.get('label', 'Your Reminder') if reminder_display else
                    'Your Reminder'
                )
                msg.html = f"""
                <html>
                <body>
                    <h2>EZCare Reminder</h2>
                    <p>This is a reminder for: <strong>{reminder_label}</strong></p>
                    <p>Please check your EZCare dashboard for more details.</p>
                    <hr>
                    <p><small>© {current_year} EZCare. All rights reserved.</small></p>
                </body>
                </html>
                """
                msg.body = f"This is a reminder for: {reminder_label}. Check your dashboard for more details."

        mail.send(msg)
        logger.info(f"Email sent to {recipients} - Subject: {subject}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise RuntimeError("Failed to send email") from e