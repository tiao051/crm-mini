"""Data Service - Handles JSON file operations for customer data."""

import json
import os
from typing import List, Optional

from models.customer import Customer


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
            os.makedirs(data_dir)
            print(f"Created data directory: {data_dir}")
    
    def load_data(self) -> List[Customer]:
        """Load customer data from JSON file (returns empty list on error)."""
        try:
            if not os.path.exists(self.data_path):
                print(f"Data file not found: {self.data_path}")
                print("Starting with empty customer list.")
                return []
            
            with open(self.data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            customers_data = data.get("customers", [])
            
            customers = []
            for customer_dict in customers_data:
                try:
                    customer = Customer.from_dict(customer_dict)
                    customers.append(customer)
                except Exception as e:
                    print(f"Error parsing customer: {e}")
                    continue
            
            print(f"Successfully loaded {len(customers)} customers from {self.data_path}")
            return customers
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {self.data_path}")
            print(f"Details: {e}")
            return []
            
        except PermissionError:
            print(f"Error: Permission denied reading {self.data_path}")
            return []
            
        except Exception as e:
            print(f"Unexpected error loading data: {e}")
            return []
    
    def save_data(self, customers: List[Customer]) -> bool:
        """Save customer data to JSON file with pretty printing."""
        try:
            self._ensure_data_directory()
            
            data = {
                "customers": [customer.to_dict() for customer in customers]
            }
            
            with open(self.data_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            print(f"Successfully saved {len(customers)} customers to {self.data_path}")
            return True
            
        except PermissionError:
            print(f"Error: Permission denied writing to {self.data_path}")
            return False
            
        except Exception as e:
            print(f"Unexpected error saving data: {e}")
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
            
            print(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def data_file_exists(self) -> bool:
        """Check if the data file exists."""
        return os.path.exists(self.data_path)
