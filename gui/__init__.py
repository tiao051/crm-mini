# GUI package
# Contains all Tkinter GUI components for the CRM application

from .main_window import MainWindow
from .customer_form import CustomerFormDialog
from .interaction_form import InteractionFormDialog
from .chart_frame import ChartFrame

__all__ = [
    'MainWindow',
    'CustomerFormDialog',
    'InteractionFormDialog',
    'ChartFrame'
]
