"""Email templates for the CRM system."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class EmailTemplate:
    """Represents an email template."""
    id: str
    name: str
    subject: str
    body: str
    
    def render(self, **variables) -> tuple:
        """
        Render template with variables.
        Returns (subject, body) with variables substituted.
        
        Variables should be in format {variable_name}
        Common variables: {customer_name}, {email}, {phone}, {customer_type}
        """
        subject = self.subject
        body = self.body
        
        for key, value in variables.items():
            subject = subject.replace(f"{{{key}}}", str(value))
            body = body.replace(f"{{{key}}}", str(value))
        
        return subject, body


# Pre-defined templates
TEMPLATES: Dict[str, EmailTemplate] = {
    "welcome": EmailTemplate(
        id="welcome",
        name="Welcome New Customer",
        subject="Welcome to Our Service, {customer_name}!",
        body="""Hello {customer_name},

Thank you for becoming our valued customer! We're excited to have you on board.

If you have any questions or need assistance, please don't hesitate to reach out.
We're here to help!

Best regards,
The CRM Team"""
    ),
    
    "follow_up": EmailTemplate(
        id="follow_up",
        name="Follow-up Check-in",
        subject="Following Up - {customer_name}",
        body="""Hi {customer_name},

I hope you're doing well! I wanted to reach out and check in with you.

Is there anything I can help you with today? Feel free to reply to this email.

Looking forward to hearing from you!

Best regards,
The CRM Team"""
    ),
    
    "offer": EmailTemplate(
        id="offer",
        name="Special Offer",
        subject="Special Offer for You, {customer_name}!",
        body="""Hello {customer_name},

We have an exclusive offer just for you! As a valued {customer_type}, 
we'd like to offer you a special discount on our products and services.

This offer is valid for a limited time only, so please don't miss out!

Click below to learn more:
[Your offer link here]

Best regards,
The CRM Team"""
    ),
    
    "birthday": EmailTemplate(
        id="birthday",
        name="Birthday Greeting",
        subject="Happy Birthday, {customer_name}!",
        body="""Hello {customer_name},

Happy Birthday! 🎉

We hope you have a wonderful day! As our valued customer, 
we'd like to offer you a special birthday gift.

Thank you for your continued support!

Best regards,
The CRM Team"""
    ),
    
    "survey": EmailTemplate(
        id="survey",
        name="Customer Feedback Survey",
        subject="We'd Love Your Feedback, {customer_name}",
        body="""Hi {customer_name},

We'd like to hear from you! Your feedback is valuable to us and helps us 
improve our services.

Please take a few minutes to share your thoughts:
[Survey link here]

Thank you!

Best regards,
The CRM Team"""
    ),
    
    "custom": EmailTemplate(
        id="custom",
        name="Custom Email",
        subject="Message for {customer_name}",
        body="""Hello {customer_name},

[Your custom message here]

Best regards,
The CRM Team"""
    ),
}


def get_template(template_id: str) -> EmailTemplate:
    """Get template by ID."""
    return TEMPLATES.get(template_id, TEMPLATES["custom"])


def get_template_names() -> List[str]:
    """Get list of all template names for dropdown."""
    return [f"{t.name}" for t in TEMPLATES.values()]


def get_template_ids() -> List[str]:
    """Get list of all template IDs."""
    return list(TEMPLATES.keys())
