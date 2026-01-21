"""Email service for sending emails via SMTP."""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict
import os

from .email_templates import EmailTemplate


class EmailConfig:
    """Configuration for SMTP email sending."""
    
    def __init__(self):
        self.config_file = "./data/email_config.json"
        self.settings = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load email config from file, or return defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading email config: {e}")
        
        # Return default config (Gmail)
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",  # App password, not real password
            "sender_name": "CRM System"
        }
    
    def save_config(self, settings: Dict) -> bool:
        """Save email config to file."""
        try:
            # Don't save password to file for security
            safe_settings = settings.copy()
            safe_settings["sender_password"] = ""
            
            with open(self.config_file, 'w') as f:
                json.dump(safe_settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving email config: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(
            self.settings.get("sender_email") and
            self.settings.get("sender_password")
        )


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.config = EmailConfig()
        self.email_log = "./data/email_log.json"
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        recipient_name: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Send an email.
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject
            body: Email body
            recipient_name: Recipient's name (optional)
        
        Returns:
            (success: bool, message: str)
        """
        if not self.config.is_configured():
            return False, "Email not configured. Please set up SMTP settings first."
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.settings['sender_name']} <{self.config.settings['sender_email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect and send
            with smtplib.SMTP(
                self.config.settings['smtp_server'],
                self.config.settings['smtp_port'],
                timeout=10
            ) as server:
                server.starttls()
                server.login(
                    self.config.settings['sender_email'],
                    self.config.settings['sender_password']
                )
                server.send_message(msg)
            
            # Log the email
            self._log_email(recipient_email, recipient_name, subject)
            
            return True, f"Email sent successfully to {recipient_email}"
        
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check email and password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def send_bulk_email(
        self,
        recipients: List[tuple[str, str]],  # [(email, name), ...]
        subject: str,
        body: str
    ) -> tuple[int, int, List[str]]:
        """
        Send email to multiple recipients.
        
        Args:
            recipients: List of (email, name) tuples
            subject: Email subject
            body: Email body
        
        Returns:
            (success_count, fail_count, error_messages)
        """
        success_count = 0
        fail_count = 0
        errors = []
        
        for email, name in recipients:
            success, message = self.send_email(email, subject, body, name)
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"{email}: {message}")
        
        return success_count, fail_count, errors
    
    def _log_email(self, recipient_email: str, recipient_name: Optional[str], subject: str):
        """Log sent email to file."""
        try:
            log_data = []
            
            # Load existing log
            if os.path.exists(self.email_log):
                with open(self.email_log, 'r') as f:
                    log_data = json.load(f)
            
            # Add new entry
            log_data.append({
                "timestamp": datetime.now().isoformat(),
                "recipient_email": recipient_email,
                "recipient_name": recipient_name or "Unknown",
                "subject": subject
            })
            
            # Save log
            with open(self.email_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        except Exception as e:
            print(f"Error logging email: {e}")
    
    def get_email_log(self, limit: int = 50) -> List[Dict]:
        """Get recent sent emails log."""
        try:
            if not os.path.exists(self.email_log):
                return []
            
            with open(self.email_log, 'r') as f:
                log_data = json.load(f)
            
            # Return most recent emails first
            return log_data[-limit:][::-1]
        
        except Exception as e:
            print(f"Error reading email log: {e}")
            return []
