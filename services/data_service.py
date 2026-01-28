"""Data Service - Handles JSON file operations for customer data."""

import json
import os
import logging
from typing import List, Optional

from models.customer import Customer

logger = logging.getLogger(__name__)


class DataService:
    """Manages customer data persistence using JSON files."""
    
    DEFAULT_DATA_PATH = "./data/customers.json"
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize with optional custom data file path."""
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        data_dir = os.path.dirname(self.data_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"Created data directory: {data_dir}")
    
    def load_data(self) -> List[Customer]:
        """Load customer data from JSON file (returns empty list on error)."""
        try:
            if not os.path.exists(self.data_path):
                logger.warning(f"Data file not found: {self.data_path}")
                return []
            
            with open(self.data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            customers = [
                Customer.from_dict(customer_dict)
                for customer_dict in data.get("customers", [])
                if self._is_valid_customer(customer_dict)
            ]
            
            logger.info(f"Loaded {len(customers)} customers from {self.data_path}")
            return customers
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.data_path}: {e}")
            return []
        except PermissionError:
            logger.error(f"Permission denied reading {self.data_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return []
    
    def _is_valid_customer(self, customer_dict: dict) -> bool:
        """Check if customer data is valid."""
        try:
            Customer.from_dict(customer_dict)
            return True
        except Exception as e:
            logger.debug(f"Invalid customer data: {e}")
            return False
    
    def save_data(self, customers: List[Customer]) -> bool:
        """Save customer data to JSON file."""
        try:
            self._ensure_data_directory()
            
            data = {"customers": [customer.to_dict() for customer in customers]}
            
            with open(self.data_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(customers)} customers to {self.data_path}")
            return True
            
        except PermissionError:
            logger.error(f"Permission denied writing to {self.data_path}")
            return False
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def backup_data(self) -> bool:
        """Create a backup of the data file."""
        try:
            if not os.path.exists(self.data_path):
                return True
            
            backup_path = f"{self.data_path}.backup"
            with open(self.data_path, 'r', encoding='utf-8') as source:
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(source.read())
            
            logger.debug(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def data_file_exists(self) -> bool:
        """Check if the data file exists."""
        return os.path.exists(self.data_path)
