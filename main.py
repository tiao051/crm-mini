import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

from utils.logger import logger

# Get module logger
module_logger = logging.getLogger(__name__)

APP_NAME = "Mini CRM"
APP_TITLE = f"{APP_NAME} - Customer Relationship Management"

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def check_dependencies() -> bool:
    """Check if required packages are installed."""
    packages = ["pandas", "openpyxl", "matplotlib", "faker"]
    missing = []
    
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        module_logger.error(f"Missing dependencies: {', '.join(missing)}")
        module_logger.error(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def initialize_data() -> None:
    """Initialize mock data if needed."""
    from utils.mock_data import initialize_mock_data
    initialize_mock_data(include_birthday_customer=False)


def main():
    """Main entry point for the CRM application."""
    try:
        module_logger.info(f"Starting {APP_TITLE}")
        
        if not check_dependencies():
            module_logger.critical("Cannot start: missing dependencies")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        os.chdir(project_root)
        module_logger.info(f"Working directory: {project_root}")
        
        initialize_data()
        module_logger.info("Data initialization complete")
        
        # Launch GUI
        from gui.main_window import MainWindow
        
        root = tk.Tk()
        app = MainWindow(root)
        module_logger.info("Application started successfully")
        app.run()
        
    except Exception as e:
        module_logger.exception(f"Critical error: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error",
            f"Failed to start {APP_NAME}:\n\n{str(e)}"
        )
        raise


if __name__ == "__main__":
    main()
