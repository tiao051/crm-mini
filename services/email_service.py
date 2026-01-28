"""Email service for sending emails via SMTP."""

import smtplib
import json
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from dotenv import load_dotenv

from .email_templates import EmailTemplate

logger = logging.getLogger(__name__)

# Email Defaults
DEFAULT_SENDER_NAME = "CRM System"
DEFAULT_SMTP_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class EmailConfig:
    """Configuration for SMTP email sending from environment and local config."""
    
    CONFIG_FILE = "./data/email_config.json"
    
    def __init__(self):
        self.settings = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load email config from .env and local file."""
        config = {
            "smtp_server": os.getenv("SMTP_SERVER", DEFAULT_SMTP_SERVER),
            "smtp_port": int(os.getenv("SMTP_PORT", DEFAULT_SMTP_PORT)),
            "sender_email": os.getenv("SENDER_EMAIL", ""),
            "sender_password": os.getenv("SENDER_PASSWORD", ""),
            "sender_name": DEFAULT_SENDER_NAME,
        }
        
        # Load sender_name from local file if exists
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    user_config = json.load(f)
                    config["sender_name"] = user_config.get("sender_name", DEFAULT_SENDER_NAME)
            except Exception as e:
                logger.error(f"Failed to load email config file: {e}")
        
        # Log missing credentials
        if not config["sender_password"]:
            logger.warning("SENDER_PASSWORD not configured in .env")
        if not config["sender_email"]:
            logger.warning("SENDER_EMAIL not configured in .env")
        else:
            logger.debug(f"Loaded SMTP config for: {config['sender_email']}")
        
        return config
    
    def save_config(self, settings: Dict) -> bool:
        """Save sender_name to local file."""
        try:
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump({"sender_name": settings.get("sender_name", DEFAULT_SENDER_NAME)}, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save email config: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(self.settings.get("sender_email") and self.settings.get("sender_password"))
    
    def get_missing_config(self) -> str:
        """Return missing config info for debugging."""
        missing = []
        if not self.settings.get("sender_email"):
            missing.append("SENDER_EMAIL not configured in .env")
        if not self.settings.get("sender_password"):
            missing.append("SENDER_PASSWORD not configured in .env")
        return "\n".join(missing)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.config = EmailConfig()
        self.email_log = "./data/email_log.json"
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        recipient_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send a single email.
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject
            body: Email body
            recipient_name: Recipient's name (optional)
        
        Returns:
            (success, message)
        """
        if not self.config.is_configured():
            missing = self.config.get_missing_config()
            error_msg = f"Email not configured:\n{missing}\n\nGo to: Marketing → Email Settings"
            return False, error_msg
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.settings['sender_name']} <{self.config.settings['sender_email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.config.settings['smtp_server'], self.config.settings['smtp_port'], timeout=10) as server:
                server.starttls()
                server.login(self.config.settings['sender_email'], self.config.settings['sender_password'])
                server.send_message(msg)
            
            self._log_email(recipient_email, recipient_name, subject)
            logger.info(f"Email sent to {recipient_email}")
            return True, f"Email sent successfully to {recipient_email}"
        
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False, "Authentication failed. Check credentials."
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False, f"Error sending email: {str(e)}"
    
    def send_bulk_email(
        self,
        recipients: List[Tuple[str, str]],
        subject: str,
        body: str
    ) -> Tuple[int, int, List[str]]:
        """Send email to multiple recipients and return statistics."""
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
        
        logger.info(f"Email blast complete: {success_count} sent, {fail_count} failed")
        return success_count, fail_count, errors
    
    def _log_email(self, recipient_email: str, recipient_name: Optional[str], subject: str) -> None:
        """Log sent email to file."""
        try:
            os.makedirs(os.path.dirname(self.email_log), exist_ok=True)
            
            log_data = []
            if os.path.exists(self.email_log):
                with open(self.email_log, 'r') as f:
                    log_data = json.load(f)
            
            log_data.append({
                "timestamp": datetime.now().isoformat(),
                "recipient_email": recipient_email,
                "recipient_name": recipient_name or "Unknown",
                "subject": subject
            })
            
            with open(self.email_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to log email: {e}")
    
    def get_email_log(self, limit: int = 50) -> List[Dict]:
        """Get recent sent emails log."""
        try:
            if not os.path.exists(self.email_log):
                return []
            
            with open(self.email_log, 'r') as f:
                log_data = json.load(f)
            
            return log_data[-limit:][::-1]
        
        except Exception as e:
            logger.error(f"Failed to read email log: {e}")
            return []
