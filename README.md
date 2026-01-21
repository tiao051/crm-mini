# Mini CRM - Customer Relationship Management System

A complete desktop Customer Relationship Management application built with Python for university project "Topic 20".

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Architecture](#architecture)
8. [Data Model](#data-model)
9. [Validation Rules](#validation-rules)
10. [API Reference](#api-reference)
11. [Screenshots](#screenshots)
12. [Contributing](#contributing)
13. [License](#license)

---

## Overview

Mini CRM is a desktop application designed to help small businesses manage their customer relationships effectively. The system provides comprehensive tools for tracking customer information, recording interactions, analyzing customer distribution, and executing marketing campaigns.

### Key Capabilities

- Full CRUD operations for customer management
- Real-time search and filtering
- Customer interaction history tracking
- Birthday reminder notifications
- Bulk email campaign simulation
- Excel report generation
- Interactive statistical visualizations

---

## Features

### Customer Management

| Feature | Description |
|---------|-------------|
| Add Customer | Create new customer records with full validation |
| Edit Customer | Modify existing customer information |
| Delete Customer | Remove customers with confirmation dialog |
| View All | Display customers in sortable table view |

### Customer Fields

- **ID**: Auto-generated unique identifier (format: CUS001, CUS002, etc.)
- **Name**: Customer's full name (2+ characters, letters only)
- **Phone**: Contact number (9-15 digits, international format supported)
- **Email**: Valid email address (regex validated)
- **Customer Type**: Classification as VIP or Potential
- **Address**: Full address with city/region
- **Date of Birth**: Birth date in YYYY-MM-DD format
- **Interaction History**: List of dated interaction records

### Search and Filter

- **Search**: Real-time filtering by name, phone, or email (case-insensitive)
- **Filter**: Quick filter by customer type (All, VIP, Potential)
- **Sort**: Click column headers to sort data

### CRM Features

- **Birthday Reminder**: Automatic check on application startup alerts users about customers with birthdays on the current date
- **Email Blast**: Simulate sending bulk marketing emails to customer groups (VIP, Potential, or All)

### Reporting

- **Excel Export**: Generate .xlsx files using pandas with customer data including region analysis and interaction counts
- **Statistical Charts**: Interactive pie and bar charts showing customer distribution by type or region

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.10+ | Core application logic |
| GUI Framework | Tkinter | Built-in | Desktop user interface |
| Data Storage | JSON | - | Persistent data storage |
| Data Processing | pandas | 2.0.0+ | Excel export and data manipulation |
| Excel Engine | openpyxl | 3.1.0+ | Write .xlsx files |
| Visualization | matplotlib | 3.7.0+ | Chart generation |
| Mock Data | Faker | 18.0.0+ | Realistic test data generation |

---

## Project Structure

```
crm-mini/
|
|-- main.py                     # Application entry point
|-- requirements.txt            # Python dependencies
|-- README.md                   # Project documentation
|
|-- data/
|   |-- customers.json          # Customer data storage (auto-generated)
|
|-- exports/                    # Excel export output directory
|
|-- models/
|   |-- __init__.py             # Package initializer
|   |-- customer.py             # Customer data class
|   |-- interaction.py          # Interaction data class
|
|-- services/
|   |-- __init__.py             # Package initializer
|   |-- data_service.py         # JSON file I/O operations
|   |-- crm_service.py          # Business logic (CRUD, search, filter)
|   |-- report_service.py       # Excel export and chart generation
|   |-- validation.py           # Input validation with regex
|
|-- gui/
|   |-- __init__.py             # Package initializer
|   |-- main_window.py          # Main application window
|   |-- customer_form.py        # Add/Edit customer dialog
|   |-- interaction_form.py     # Interaction management dialog
|   |-- chart_frame.py          # Embedded matplotlib charts
|
|-- utils/
    |-- __init__.py             # Package initializer
    |-- mock_data.py            # Mock data generator using Faker
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Tkinter (included with Python on Windows and most Linux distributions)

### Step-by-Step Installation

1. **Clone or download the repository**

   ```bash
   git clone <repository-url>
   cd crm-mini
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

### Dependencies

The following packages will be installed:

```
pandas>=2.0.0
openpyxl>=3.1.0
matplotlib>=3.7.0
faker>=18.0.0
```

---

## Usage

### Starting the Application

```bash
cd crm-mini
python main.py
```

On first run, the application will:
1. Check for required dependencies
2. Create the data directory if it does not exist
3. Generate 25 mock customers with realistic data
4. Launch the main window
5. Check for customer birthdays and display alerts if any

### Basic Operations

#### Adding a Customer

1. Click the "Add New" button or use the Customers menu
2. Fill in all required fields (marked with asterisk)
3. Select customer type (VIP or Potential)
4. Click "Save Customer"

#### Editing a Customer

1. Select a customer row in the table
2. Double-click the row or click the "Edit" button
3. Modify the desired fields
4. Click "Save Customer"

#### Deleting a Customer

1. Select a customer row in the table
2. Click the "Delete" button
3. Confirm the deletion in the dialog

#### Managing Interactions

1. Select a customer row
2. Click the "Interactions" button
3. View existing interactions or add new ones
4. Delete interactions as needed

#### Searching and Filtering

- Type in the search box to filter by name, phone, or email
- Use the filter dropdown to show only VIP or Potential customers
- Click column headers to sort the table

#### Exporting to Excel

1. Click the "Export" button
2. Choose a location and filename
3. The current filtered view will be exported

#### Email Blast Simulation

1. Click the "Email Blast" button
2. Select target group (All, VIP, or Potential)
3. Click "Send Blast" to simulate the campaign

---

## Architecture

### Design Patterns

The application follows these software design principles:

- **Model-View-Controller (MVC)**: Separation of data models, business logic, and user interface
- **Single Responsibility Principle**: Each class handles one specific concern
- **Dependency Injection**: Services receive their dependencies through constructors

### Layer Architecture

```
+------------------+
|   GUI Layer      |  Tkinter windows and dialogs
+------------------+
        |
        v
+------------------+
| Service Layer    |  Business logic, validation, reporting
+------------------+
        |
        v
+------------------+
|   Data Layer     |  JSON file operations
+------------------+
        |
        v
+------------------+
|   Model Layer    |  Data classes (Customer, Interaction)
+------------------+
```

### Class Diagram

```
Customer
  - id: str
  - name: str
  - phone: str
  - email: str
  - customer_type: str
  - address: str
  - date_of_birth: str
  - interactions: List[Interaction]
  + to_dict(): dict
  + from_dict(data): Customer
  + add_interaction(date, content): void
  + get_region(): str

Interaction
  - date: str
  - content: str
  + to_dict(): dict
  + from_dict(data): Interaction

DataService
  - data_path: str
  + load_data(): List[Customer]
  + save_data(customers): bool
  + backup_data(): bool

CRMService
  - customers: List[Customer]
  - data_service: DataService
  + add_customer(...): Tuple[bool, str, Customer]
  + update_customer(...): Tuple[bool, str]
  + delete_customer(id): Tuple[bool, str]
  + search_customers(query): List[Customer]
  + filter_by_type(type): List[Customer]
  + check_birthdays(): List[Customer]
  + simulate_email_blast(type): Tuple[int, List[str]]

ReportService
  + export_to_excel(customers, filename): Tuple[bool, str]
  + create_customer_type_chart(stats, type): Figure
  + create_region_chart(stats, type): Figure
```

---

## Data Model

### JSON Schema

The customer data is stored in `data/customers.json` with the following structure:

```json
{
  "customers": [
    {
      "id": "CUS001",
      "name": "John Smith",
      "phone": "+1-555-123-4567",
      "email": "john.smith@example.com",
      "customer_type": "VIP",
      "address": "123 Main Street, New York, NY",
      "date_of_birth": "1985-06-15",
      "interactions": [
        {
          "date": "2024-01-15",
          "content": "Called about product inquiry"
        },
        {
          "date": "2024-02-20",
          "content": "Placed order #12345"
        }
      ]
    }
  ]
}
```

### Field Specifications

| Field | Type | Required | Format | Example |
|-------|------|----------|--------|---------|
| id | string | Yes | CUSxxx | CUS001 |
| name | string | Yes | 2+ chars | John Smith |
| phone | string | Yes | 9-15 digits | +1-555-123-4567 |
| email | string | Yes | valid email | john@example.com |
| customer_type | string | Yes | VIP or Potential | VIP |
| address | string | No | free text | 123 Main St, City, State |
| date_of_birth | string | Yes | YYYY-MM-DD | 1985-06-15 |
| interactions | array | No | list of objects | see above |

---

## Validation Rules

### Email Validation

Regular expression pattern:
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

Valid examples:
- user@example.com
- john.doe@company.org
- name+tag@domain.co.uk

### Phone Validation

After removing formatting characters (spaces, dashes, parentheses):
```
^\+?[0-9]{9,15}$
```

Valid examples:
- 0901234567
- +1-555-123-4567
- (555) 123-4567

### Date Validation

Format: YYYY-MM-DD

Constraints:
- Year: 1900-2100
- Month: 01-12
- Day: 01-31 (validated per month)

### Name Validation

Pattern:
```
^[a-zA-Z\s\-'\.]+$
```

Constraints:
- Minimum 2 characters
- Only letters, spaces, hyphens, apostrophes, and periods

---

## API Reference

### CRMService Methods

#### add_customer

```python
def add_customer(
    name: str,
    phone: str,
    email: str,
    customer_type: str,
    address: str,
    date_of_birth: str
) -> Tuple[bool, str, Optional[Customer]]
```

Creates a new customer with the provided information.

**Returns**: Tuple containing success status, message, and customer object (if successful)

#### update_customer

```python
def update_customer(
    customer_id: str,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    customer_type: Optional[str] = None,
    address: Optional[str] = None,
    date_of_birth: Optional[str] = None
) -> Tuple[bool, str]
```

Updates an existing customer. Only provided fields are updated.

**Returns**: Tuple containing success status and message

#### delete_customer

```python
def delete_customer(customer_id: str) -> Tuple[bool, str]
```

Removes a customer by ID.

**Returns**: Tuple containing success status and message

#### search_customers

```python
def search_customers(query: str) -> List[Customer]
```

Searches customers by name, phone, or email (case-insensitive partial match).

**Returns**: List of matching customers

#### filter_by_type

```python
def filter_by_type(customer_type: str) -> List[Customer]
```

Filters customers by type.

**Parameters**: customer_type - "VIP", "Potential", or "All"

**Returns**: List of filtered customers

#### check_birthdays

```python
def check_birthdays() -> List[Customer]
```

Finds customers with birthdays matching the current date.

**Returns**: List of customers with birthdays today

#### simulate_email_blast

```python
def simulate_email_blast(customer_type: str) -> Tuple[int, List[str]]
```

Simulates sending bulk email to a customer group.

**Returns**: Tuple containing recipient count and list of email addresses

### ReportService Methods

#### export_to_excel

```python
def export_to_excel(
    customers: List[Customer],
    filename: Optional[str] = None
) -> Tuple[bool, str]
```

Exports customer data to an Excel file.

**Returns**: Tuple containing success status and filepath or error message

---

## Screenshots

The application features:

1. **Main Dashboard**: Customer table with search, filter, and action buttons
2. **Customer Form**: Modal dialog for adding/editing customers with validation
3. **Interaction Manager**: Dialog for viewing and managing customer interactions
4. **Statistics Panel**: Interactive charts showing customer distribution
5. **Export Options**: Excel export with customizable filename

---

## Error Handling

The application implements comprehensive error handling:

- **File I/O Errors**: Graceful handling of missing files, permission issues
- **Validation Errors**: Clear user feedback for invalid input
- **Data Parsing Errors**: Recovery from malformed JSON data
- **Runtime Exceptions**: Try-except blocks prevent application crashes

---

## Testing

### Manual Testing Checklist

1. Add a new customer with valid data
2. Add a customer with invalid email - verify error message
3. Edit an existing customer
4. Delete a customer with confirmation
5. Search by partial name
6. Filter by VIP type
7. Add interaction to a customer
8. Check birthday reminder function
9. Simulate email blast
10. Export to Excel and verify file contents
11. Toggle between pie and bar charts
12. Toggle between customer type and region data

---

## Known Limitations

1. Single-user application (no multi-user support)
2. Local file storage only (no cloud sync)
3. No undo/redo functionality
4. English language only
5. No automated backup scheduling

---

## Future Enhancements

Potential improvements for future versions:

- Database integration (SQLite or PostgreSQL)
- User authentication and roles
- Email integration for actual campaign sending
- Calendar integration for appointment scheduling
- Mobile-responsive web version
- Data import from CSV/Excel
- Custom reporting templates
- Automated backup to cloud storage

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 style guidelines
4. Add appropriate comments and documentation
5. Test all changes thoroughly
6. Submit a pull request with clear description

---

## License

This project is created for educational purposes as part of a university assignment (Topic 20: Customer Relationship Management).

---

## Authors

University Group Project - Topic 20

---

## Acknowledgments

- Python Software Foundation for Python and Tkinter
- pandas development team for data processing capabilities
- matplotlib development team for visualization tools
- Faker library contributors for mock data generation
