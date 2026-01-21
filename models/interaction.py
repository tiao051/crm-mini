"""Interaction Model - Represents a single interaction record with a customer."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Interaction:
    """Represents an interaction with a customer (date and content)."""
    date: str
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """Create from dictionary."""
        return cls(
            date=data.get("date", ""),
            content=data.get("content", "")
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"[{self.date}] {self.content}"
