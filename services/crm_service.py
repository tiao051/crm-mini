"""
Core business logic for the CRM application.
Provides CRUD operations, search, filter, and CRM-specific features.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from models.customer import Customer
from models.interaction import Interaction
from services.data_service import DataService
from services.validation import validate_all_customer_fields, ValidationError

logger = logging.getLogger(__name__)


class CRMService:
    """
    Main service class for CRM business logic.
    Manages customer data and provides all CRUD operations.
    """
    
    def __init__(self, data_service: Optional[DataService] = None):
        """
        Initialize the CRM Service.
        
        Args:
            data_service: Optional DataService instance.
                         Creates default one if not provided.
        """
        self.data_service = data_service or DataService()
        self.customers: List[Customer] = []
        self.load_customers()
    
    def load_customers(self) -> None:
        """Load customers from data storage."""
        self.customers = self.data_service.load_data()
    
    def save_customers(self) -> bool:
        """Save current customers to data storage."""
        return self.data_service.save_data(self.customers)
    
    def generate_customer_id(self) -> str:
        """Generate unique customer ID (format: CUS001, CUS002, etc)."""
        if not self.customers:
            return "CUS001"
        
        max_num = max(
            (int(customer.id[3:]) 
             for customer in self.customers 
             if customer.id.startswith("CUS") and len(customer.id) > 3
             and customer.id[3:].isdigit()),
            default=0
        )
        
        return f"CUS{max_num + 1:03d}"
    
    def add_customer(
        self,
        name: str,
        phone: str,
        email: str,
        customer_type: str,
        address: str,
        date_of_birth: str
    ) -> Tuple[bool, str, Optional[Customer]]:
        """Add a new customer to the system with validation."""
        is_valid, error_msg = validate_all_customer_fields(
            name, phone, email, customer_type, date_of_birth
        )
        
        if not is_valid:
            return False, error_msg, None
        
        for customer in self.customers:
            if customer.email.lower() == email.lower():
                return False, f"Email '{email}' already exists", None
        
        customer_id = self.generate_customer_id()
        
        new_customer = Customer(
            id=customer_id,
            name=name.strip(),
            phone=phone.strip(),
            email=email.strip().lower(),
            customer_type=customer_type,
            address=address.strip(),
            date_of_birth=date_of_birth,
            interactions=[]
        )
        
        self.customers.append(new_customer)
        self.save_customers()
        
        return True, f"Customer {customer_id} added successfully", new_customer
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """
        Get a customer by ID.
        
        Args:
            customer_id: The customer's unique ID
            
        Returns:
            Customer object if found, None otherwise
        """
        for customer in self.customers:
            if customer.id == customer_id:
                return customer
        return None
    
    def get_all_customers(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List of all Customer objects
        """
        return self.customers.copy()
    
    def update_customer(
        self,
        customer_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        customer_type: Optional[str] = None,
        address: Optional[str] = None,
        date_of_birth: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update an existing customer.
        
        Only updates fields that are provided (not None).
        Validates all provided fields.
        
        Args:
            customer_id: ID of customer to update
            name, phone, email, etc.: Fields to update
            
        Returns:
            Tuple of (success, message)
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return False, f"Customer {customer_id} not found"
        
        # Validate fields that are being updated
        new_name = name if name is not None else customer.name
        new_phone = phone if phone is not None else customer.phone
        new_email = email if email is not None else customer.email
        new_type = customer_type if customer_type is not None else customer.customer_type
        new_dob = date_of_birth if date_of_birth is not None else customer.date_of_birth
        
        is_valid, error_msg = validate_all_customer_fields(
            new_name, new_phone, new_email, new_type, new_dob
        )
        
        if not is_valid:
            return False, error_msg
        
        if email is not None and email.lower() != customer.email.lower():
            for c in self.customers:
                if c.id != customer_id and c.email.lower() == email.lower():
                    return False, f"Email '{email}' already exists"
        
        if name is not None:
            customer.name = name.strip()
        if phone is not None:
            customer.phone = phone.strip()
        if email is not None:
            customer.email = email.strip().lower()
        if customer_type is not None:
            customer.customer_type = customer_type
        if address is not None:
            customer.address = address.strip()
        if date_of_birth is not None:
            customer.date_of_birth = date_of_birth
        
        self.save_customers()
        return True, f"Customer {customer_id} updated successfully"
    
    def delete_customer(self, customer_id: str) -> Tuple[bool, str]:
        """
        Delete a customer by ID.
        
        Args:
            customer_id: ID of customer to delete
            
        Returns:
            Tuple of (success, message)
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return False, f"Customer {customer_id} not found"
        
        self.customers.remove(customer)
        self.save_customers()
        
        return True, f"Customer {customer_id} deleted successfully"
    
    def add_interaction(
        self,
        customer_id: str,
        date: str,
        content: str
    ) -> Tuple[bool, str]:
        """
        Add an interaction to a customer's history.
        
        Args:
            customer_id: ID of the customer
            date: Date of interaction (YYYY-MM-DD)
            content: Description of the interaction
            
        Returns:
            Tuple of (success, message)
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return False, f"Customer {customer_id} not found"
        
        if not content.strip():
            return False, "Interaction content cannot be empty"
        
        customer.add_interaction(date, content.strip())
        self.save_customers()
        
        return True, "Interaction added successfully"
    
    def delete_interaction(
        self,
        customer_id: str,
        interaction_index: int
    ) -> Tuple[bool, str]:
        """
        Delete an interaction from a customer's history.
        
        Args:
            customer_id: ID of the customer
            interaction_index: Index of interaction to delete
            
        Returns:
            Tuple of (success, message)
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return False, f"Customer {customer_id} not found"
        
        if interaction_index < 0 or interaction_index >= len(customer.interactions):
            return False, "Invalid interaction index"
        
        customer.interactions.pop(interaction_index)
        self.save_customers()
        
        return True, "Interaction deleted successfully"
    
    def search_customers(self, query: str) -> List[Customer]:
        """Search customers by name, phone, or email (case-insensitive)."""
        if not query.strip():
            return self.customers.copy()
        
        query_lower = query.lower().strip()
        
        return [
            customer for customer in self.customers
            if query_lower in customer.name.lower()
               or query in customer.phone
               or query_lower in customer.email.lower()
        ]
    
    def filter_by_type(self, customer_type: str) -> List[Customer]:
        """
        Filter customers by customer type.
        
        Args:
            customer_type: "VIP", "Potential", or "All" for no filter
            
        Returns:
            List of filtered Customer objects
        """
        if customer_type == "All" or not customer_type:
            return self.customers.copy()
        
        return [c for c in self.customers if c.customer_type == customer_type]
    
    def check_birthdays(self) -> List[Customer]:
        """Check for customers with birthdays today."""
        today = datetime.now()
        today_month_day = (today.month, today.day)
        
        birthday_customers = []
        
        for customer in self.customers:
            try:
                birth_date = datetime.strptime(customer.date_of_birth, "%Y-%m-%d")
                birth_month_day = (birth_date.month, birth_date.day)
                
                if birth_month_day == today_month_day:
                    birthday_customers.append(customer)
                    
            except ValueError:
                continue
        
        return birthday_customers
    
    def simulate_email_blast(self, customer_type: str) -> Tuple[int, List[str]]:
        """Simulate sending bulk email to a group of customers (no actual emails sent)."""
        if customer_type == "All":
            target_customers = self.customers
        else:
            target_customers = [c for c in self.customers if c.customer_type == customer_type]
        
        emails = [c.email for c in target_customers if c.email]
        
        return len(emails), emails
    
    def get_customer_type_stats(self) -> dict:
        """Get statistics on customer types."""
        stats = {"VIP": 0, "Potential": 0}
        
        for customer in self.customers:
            if customer.customer_type in stats:
                stats[customer.customer_type] += 1
        
        return stats
    
    def get_region_stats(self) -> dict:
        """Get statistics on customers by region."""
        stats = {}
        
        for customer in self.customers:
            region = customer.get_region()
            stats[region] = stats.get(region, 0) + 1
        
        return stats
