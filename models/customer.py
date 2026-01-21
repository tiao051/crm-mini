"""Customer Model - Represents a customer entity in the CRM system."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .interaction import Interaction


@dataclass
class Customer:
    """Represents a customer with basic info and interaction history."""
    id: str
    name: str
    phone: str
    email: str
    customer_type: str
    address: str
    date_of_birth: str
    interactions: List[Interaction] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Customer to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "customer_type": self.customer_type,
            "address": self.address,
            "date_of_birth": self.date_of_birth,
            "interactions": [interaction.to_dict() for interaction in self.interactions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """Create Customer from dictionary with nested interactions."""
        interactions_data = data.get("interactions", [])
        interactions = [Interaction.from_dict(i) for i in interactions_data]
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            customer_type=data.get("customer_type", "Potential"),
            address=data.get("address", ""),
            date_of_birth=data.get("date_of_birth", ""),
            interactions=interactions
        )
    
    def add_interaction(self, date: str, content: str) -> None:
        """Add a new interaction to the customer's history."""
        self.interactions.append(Interaction(date=date, content=content))
    
    def get_region(self) -> str:
        """Extract region/city from address (assumes format: '..., City, State')."""
        if not self.address:
            return "Unknown"
        
        parts = self.address.split(",")
        if len(parts) >= 2:
            return parts[-2].strip()
        elif len(parts) == 1:
            return parts[0].strip()
        return "Unknown"
    
    def __str__(self) -> str:
        """String representation of the customer."""
        return f"{self.id}: {self.name} ({self.customer_type})"
