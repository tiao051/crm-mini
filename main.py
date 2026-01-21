import sys
import os
import tkinter as tk
from tkinter import messagebox

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

SEPARATOR = "=" * 50

def print_header(title: str) -> None:
    """Print a formatted header with separator lines."""
    print(f"\n{SEPARATOR}")
    print(title)
    print(f"{SEPARATOR}\n")


def check_dependencies() -> bool:
    """Check if required packages can be imported."""
    packages = {
        "pandas": "pip install pandas",
        "openpyxl": "pip install openpyxl",
        "matplotlib": "pip install matplotlib",
        "faker": "pip install faker"
    }
    
    missing = []
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_header("Missing required dependencies!")
        print("Please install using:\n")
        print(f"pip install {' '.join(missing)}")
        print("Or run: pip install -r requirements.txt")
        print(SEPARATOR)
        return False
    
    return True


def initialize_data() -> None:
    """Initialize mock data if data file doesn't exist."""
    from utils.mock_data import initialize_mock_data
    initialize_mock_data(include_birthday_customer=False)


def main():
    """Main entry point for the Mini CRM application."""
    print_header("Mini CRM - Customer Relationship Management")
    
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    os.chdir(project_root)
    print(f"Working directory: {project_root}")
    
    print("Checking data...")
    initialize_data()
    
    print("Starting application...\n")
    
    try:
        from gui.main_window import MainWindow
        
        root = tk.Tk()
        app = MainWindow(root)
        
        print("Application started successfully!")
        print_header("Close the window to exit.")
        
        app.run()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"Failed to start Mini CRM:\n\n{str(e)}\n\n"
            "Please check the console for details."
        )
        raise


if __name__ == "__main__":
    main()
