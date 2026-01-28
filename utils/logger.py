"""Logging configuration for CRM application."""

import logging
import os
from datetime import datetime

# Create logs directory
LOGS_DIR = "./logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging
log_file = os.path.join(LOGS_DIR, f"crm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("crm_app")

