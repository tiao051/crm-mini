# Services package
# Contains business logic and data services for the CRM application

from .data_service import DataService
from .crm_service import CRMService
from .report_service import ReportService
from .validation import (
    validate_email,
    validate_phone,
    validate_date,
    ValidationError
)

__all__ = [
    'DataService',
    'CRMService', 
    'ReportService',
    'validate_email',
    'validate_phone',
    'validate_date',
    'ValidationError'
]
