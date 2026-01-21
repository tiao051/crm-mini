"""
Generates realistic mock customer data for the CRM system.
Uses the Faker library for realistic names, emails, addresses, etc.
"""

import random
from datetime import datetime, timedelta
from typing import List

# Faker is used to generate realistic fake data
# Install with: pip install faker
from faker import Faker

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.customer import Customer
from models.interaction import Interaction
from services.data_service import DataService


# Initialize Faker with English locale
fake = Faker('en_US')


def generate_customer_id(index: int) -> str:
    """Generate a customer ID in format CUS001, CUS002, etc."""
    return f"CUS{index:03d}"


def generate_phone() -> str:
    """
    Generate a valid phone number matching validation rules.
    Format: XXX-XXX-XXXX (10 digits with dashes)
    """
    # Generate 10 random digits
    digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    # Format as XXX-XXX-XXXX
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:10]}"


def generate_address() -> str:
    """
    Generate a realistic US address.
    Format: Street, City, State
    """
    return f"{fake.street_address()}, {fake.city()}, {fake.state()}"


def generate_birth_date() -> str:
    """
    Generate a random birth date.
    Age range: 18-70 years old
    Format: YYYY-MM-DD
    """
    # Generate age between 18 and 70
    age = random.randint(18, 70)
    birth_year = datetime.now().year - age
    
    # Random month and day
    birth_date = fake.date_of_birth(
        minimum_age=18,
        maximum_age=70
    )
    
    return birth_date.strftime("%Y-%m-%d")


def generate_interaction() -> Interaction:
    """
    Generate a realistic interaction record.
    Random date within the past 2 years.
    """
    # Random date within past 2 years
    days_ago = random.randint(1, 730)
    interaction_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    # Possible interaction types
    interaction_types = [
        "Called about product inquiry",
        "Placed order #" + str(random.randint(10000, 99999)),
        "Requested technical support",
        "Attended promotional event",
        "Submitted feedback via email",
        "Renewed subscription",
        "Upgraded service plan",
        "Requested product demo",
        "Complained about delivery delay",
        "Asked about warranty terms",
        "Purchased gift card",
        "Referred a new customer",
        "Scheduled consultation meeting",
        "Registered for newsletter",
        "Requested invoice copy",
        "Updated contact information",
        "Participated in survey",
        "Claimed loyalty reward points",
        "Inquired about bulk pricing",
        "Requested custom quotation"
    ]
    
    content = random.choice(interaction_types)
    
    return Interaction(date=interaction_date, content=content)


def generate_customer(index: int) -> Customer:
    """
    Generate a single realistic customer with all fields.
    
    Args:
        index: Sequential index for ID generation
        
    Returns:
        Customer object with realistic data
    """
    # Generate basic info
    customer_id = generate_customer_id(index)
    name = fake.name()
    email = fake.email()
    phone = generate_phone()
    address = generate_address()
    date_of_birth = generate_birth_date()
    
    # Randomly assign customer type (40% VIP, 60% Potential)
    customer_type = random.choices(
        ["VIP", "Potential"],
        weights=[40, 60],
        k=1
    )[0]
    
    # Generate 2-5 interactions per customer
    num_interactions = random.randint(2, 5)
    interactions = [generate_interaction() for _ in range(num_interactions)]
    
    # Sort interactions by date (oldest first)
    interactions.sort(key=lambda x: x.date)
    
    return Customer(
        id=customer_id,
        name=name,
        phone=phone,
        email=email,
        customer_type=customer_type,
        address=address,
        date_of_birth=date_of_birth,
        interactions=interactions
    )


def generate_mock_data(count: int = 25) -> List[Customer]:
    """
    Generate a list of mock customers.
    
    Args:
        count: Number of customers to generate (default: 25)
        
    Returns:
        List of Customer objects
        
    Example:
        >>> customers = generate_mock_data(25)
        >>> print(f"Generated {len(customers)} customers")
    """
    print(f"Generating {count} mock customers...")
    
    customers = []
    for i in range(1, count + 1):
        customer = generate_customer(i)
        customers.append(customer)
        print(f"  Generated: {customer.name} ({customer.customer_type})")
    
    print(f"Successfully generated {len(customers)} customers")
    return customers


def generate_birthday_customer() -> Customer:
    """
    Generate a customer whose birthday is TODAY.
    Useful for testing the birthday reminder feature.
    
    Returns:
        Customer with today's date as birthday
    """
    customer = generate_customer(999)
    
    # Set birthday to today
    today = datetime.now()
    # Keep the birth year reasonable (30-50 years ago)
    birth_year = today.year - random.randint(30, 50)
    customer.date_of_birth = f"{birth_year}-{today.month:02d}-{today.day:02d}"
    customer.id = "CUS999"
    customer.name = "Birthday Person (Test)"
    
    return customer


def initialize_mock_data(include_birthday_customer: bool = False) -> bool:
    """
    Initialize the data file with mock customer data.
    
    Only creates data if the file doesn't exist.
    
    Args:
        include_birthday_customer: If True, adds a customer with today's birthday
        
    Returns:
        True if data was created, False if file already exists
    """
    data_service = DataService()
    
    if data_service.data_file_exists():
        print("Data file already exists. Skipping mock data generation.")
        print("Delete './data/customers.json' to regenerate mock data.")
        return False
    
    # Generate 25 customers
    customers = generate_mock_data(25)
    
    # Optionally add a birthday customer for testing
    if include_birthday_customer:
        birthday_customer = generate_birthday_customer()
        customers.append(birthday_customer)
        print(f"Added birthday test customer: {birthday_customer.name}")
    
    # Save to file
    success = data_service.save_data(customers)
    
    if success:
        print("\n Mock data initialization complete!")
        print(f"   Total customers: {len(customers)}")
        
        # Count by type
        vip_count = sum(1 for c in customers if c.customer_type == "VIP")
        potential_count = sum(1 for c in customers if c.customer_type == "Potential")
        print(f"   VIP customers: {vip_count}")
        print(f"   Potential customers: {potential_count}")
        
    return success


# Run directly to generate mock data
if __name__ == "__main__":
    print("=" * 50)
    print("Mock Data Generator for Mini CRM")
    print("=" * 50)
    
    # Parse command line args
    include_birthday = "--birthday" in sys.argv
    
    success = initialize_mock_data(include_birthday_customer=include_birthday)
    
    if success:
        print("\nMock data saved to './data/customers.json'")
    else:
        print("\nNo new data generated.")
