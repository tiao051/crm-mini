"""
Provides input validation utilities using regex patterns.
Includes validation for email, phone, and date formats.
"""

import re
from typing import Tuple


class ValidationError(Exception):
    """
    Custom exception for validation errors.
    Contains the field name and error message.
    """
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format."""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, ""
    else:
        return False, "Invalid email format (e.g., name@example.com)"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number format (9-15 digits with optional + and formatting)."""
    if not phone:
        return False, "Phone number is required"
    
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    pattern = r'^\+?[0-9]{9,15}$'
    
    if re.match(pattern, cleaned):
        return True, ""
    else:
        return False, "Invalid phone format (9-15 digits, may include +, -, spaces)"


def validate_date(date_str: str) -> Tuple[bool, str]:
    """Validate date string in YYYY-MM-DD format with range checks."""
    if not date_str:
        return False, "Date is required"
    
    pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    
    match = re.match(pattern, date_str)
    if not match:
        return False, "Invalid date format (use YYYY-MM-DD)"
    
    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
    
    if not (1900 <= year <= 2100):
        return False, "Year must be between 1900 and 2100"
    
    if not (1 <= month <= 12):
        return False, "Month must be between 1 and 12"
    
    if not (1 <= day <= 31):
        return False, "Day must be between 1 and 31"
    
    days_in_month = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    if day > days_in_month[month]:
        return False, f"Day {day} is invalid for month {month}"
    
    return True, ""


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate customer name (min 2 chars, letters/spaces/hyphens/apostrophes)."""
    if not name:
        return False, "Name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    pattern = r"^[a-zA-Z\s\-'\.]+$"
    
    if not re.match(pattern, name):
        return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, ""


def validate_customer_type(customer_type: str) -> Tuple[bool, str]:
    """Validate customer type (must be 'VIP' or 'Potential')."""
    valid_types = ["VIP", "Potential"]
    
    if not customer_type:
        return False, "Customer type is required"
    
    if customer_type not in valid_types:
        return False, f"Customer type must be one of: {', '.join(valid_types)}"
    
    return True, ""


def validate_all_customer_fields(
    name: str,
    phone: str,
    email: str,
    customer_type: str,
    date_of_birth: str
) -> Tuple[bool, str]:
    """
    Validate all required customer fields.
    
    Args:
        name: Customer name
        phone: Phone number
        email: Email address
        customer_type: VIP or Potential
        date_of_birth: Date of birth
        
    Returns:
        Tuple of (all_valid, first_error_message)
    """
    # Validate each field
    validations = [
        ("Name", validate_name(name)),
        ("Phone", validate_phone(phone)),
        ("Email", validate_email(email)),
        ("Customer Type", validate_customer_type(customer_type)),
        ("Date of Birth", validate_date(date_of_birth))
    ]
    
    for field_name, (is_valid, error_msg) in validations:
        if not is_valid:
            return False, f"{field_name}: {error_msg}"
    
    return True, ""
