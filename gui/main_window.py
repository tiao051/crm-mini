"""Main application window for the Mini CRM system."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from datetime import datetime
import os
import re
from difflib import SequenceMatcher

from models.customer import Customer
from services.crm_service import CRMService
from services.report_service import ReportService
from services.data_service import DataService
from services.email_service import EmailService
from gui.customer_form import CustomerFormDialog
from gui.interaction_form import InteractionFormDialog
from gui.chart_frame import ChartFrame
from gui.email_dialog import EmailDialog, EmailSettingsDialog
from services.email_service import EmailService


class MainWindow:
    """Main application window with customer table, search, and chart."""
    
    COLORS = {
        'bg': '#f0f2f5',
        'card': '#ffffff',
        'primary': '#6366f1',
        'primary_dark': '#4f46e5',
        'text': '#1f2937',
        'text_muted': '#6b7280',
        'border': '#e5e7eb',
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mini CRM - Customer Relationship Management")
        # Set window to fullscreen
        self.root.state('zoomed')  # Windows/Linux
        self.root.configure(bg=self.COLORS['bg'])
        # Bind resize event to handle layout adjustments
        self.root.bind('<Configure>', self._on_window_resize)
        
        self.data_service = DataService()
        self.crm_service = CRMService(self.data_service)
        self.report_service = ReportService()
        self.email_service = EmailService()
        
        self.current_filter = "All"
        self.current_search = ""
        self.last_width = self.root.winfo_screenwidth()
        self.last_height = self.root.winfo_screenheight()
        self.is_responsive_mode = self.last_width < 1200  # Flag for single column layout
        
        self._apply_theme()
        self._create_menu()
        self._create_widgets()
        self._refresh_table()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Force geometry calculation and update chart after window is fully rendered
        self.root.update_idletasks()
        self.root.after(200, self._update_chart)
    
    def _get_responsive_font_size(self, base_size: int) -> int:
        """Calculate responsive font size based on window width."""
        current_width = self.root.winfo_width()
        if current_width < 1000:
            return max(int(base_size * 0.85), 8)
        elif current_width < 1200:
            return int(base_size * 0.9)
        return base_size
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for fuzzy search: lowercase, remove accents and special chars."""
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove special characters and extra spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.strip()
    
    def _fuzzy_match(self, search_text: str, target_text: str, threshold: float = 0.6) -> bool:
        """
        Fuzzy match search text against target text.
        Returns True if similarity >= threshold or if search is substring of target.
        """
        search_norm = self._normalize_text(search_text)
        target_norm = self._normalize_text(target_text)
        
        if not search_norm:
            return True
        
        # Exact substring match (most important)
        if search_norm in target_norm:
            return True
        
        # Fuzzy match using sequence matching
        ratio = SequenceMatcher(None, search_norm, target_norm).ratio()
        return ratio >= threshold
    
    def _apply_theme(self) -> None:
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        title_font_size = self._get_responsive_font_size(20)
        subtitle_font_size = self._get_responsive_font_size(12)
        label_font_size = self._get_responsive_font_size(10)
        
        style.configure("TFrame", background=self.COLORS['bg'])
        style.configure("TLabel", background=self.COLORS['bg'], foreground=self.COLORS['text'], font=('Segoe UI', label_font_size))
        style.configure("Title.TLabel", font=('Segoe UI', title_font_size, 'bold'), foreground=self.COLORS['text'])
        style.configure("Subtitle.TLabel", font=('Segoe UI', subtitle_font_size), foreground=self.COLORS['text_muted'])
        
        style.configure("Modern.TButton", font=('Segoe UI', 10, 'bold'), padding=(16, 10))
        
        style.configure("Custom.Treeview", font=('Segoe UI', 10), rowheight=36,
                       background=self.COLORS['card'], foreground=self.COLORS['text'],
                       fieldbackground=self.COLORS['card'], borderwidth=0)
        style.configure("Custom.Treeview.Heading", font=('Segoe UI', 10, 'bold'),
                       background='#f3f4f6', foreground=self.COLORS['text'], padding=(10, 8))
        style.map("Custom.Treeview", background=[('selected', self.COLORS['primary'])],
                 foreground=[('selected', 'white')])
    
    def _create_menu(self) -> None:
        menubar = tk.Menu(self.root, bg='white', fg=self.COLORS['text'])
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Data", command=self._refresh_table)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Excel...", command=self._export_to_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        customers_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Customers", menu=customers_menu)
        customers_menu.add_command(label="Add Customer", command=self._show_add_dialog)
        customers_menu.add_command(label="Edit Customer", command=self._show_edit_dialog)
        customers_menu.add_command(label="Delete Customer", command=self._delete_customer)
        customers_menu.add_separator()
        customers_menu.add_command(label="View Interactions", command=self._show_interactions_dialog)
        
        marketing_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Marketing", menu=marketing_menu)
        marketing_menu.add_command(label="Send Email to Customer", command=self._send_email_to_selected)
        marketing_menu.add_command(label="Email Blast - All", command=lambda: self._email_blast("All"))
        marketing_menu.add_command(label="Email Blast - VIP", command=lambda: self._email_blast("VIP"))
        marketing_menu.add_command(label="Email Blast - Potential", command=lambda: self._email_blast("Potential"))
        marketing_menu.add_separator()
        marketing_menu.add_command(label="Email Settings", command=self._show_email_settings)
        marketing_menu.add_command(label="View Email Log", command=self._show_email_log)
        marketing_menu.add_command(label="Email Blast - Potential", command=lambda: self._email_blast("Potential"))
        marketing_menu.add_separator()
        marketing_menu.add_command(label="Check Birthdays", command=self._check_birthdays)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_widgets(self) -> None:
        # Responsive padding based on window size
        current_width = self.root.winfo_width()
        padx = 15 if current_width < 1000 else 20
        pady = 10 if current_width < 1000 else 15
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Responsive header layout
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(title_frame, text="Mini CRM Dashboard", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(title_frame, text="Manage your customer relationships effectively",
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side=tk.RIGHT, padx=(10, 0))
        count_font_size = self._get_responsive_font_size(14)
        self.count_label = ttk.Label(stats_frame, text="25 customers",
                                     font=('Segoe UI', count_font_size, 'bold'), foreground=self.COLORS['primary'])
        self.count_label.pack(side=tk.RIGHT)
        
        search_card = tk.Frame(main_frame, bg=self.COLORS['card'],
                              highlightbackground=self.COLORS['border'], highlightthickness=1)
        search_card.pack(fill=tk.X, pady=(0, 15))
        
        search_inner = ttk.Frame(search_card)
        search_inner.pack(fill=tk.X, padx=15, pady=12)
        
        # Responsive search layout - wrap on small screens
        current_width = self.root.winfo_width()
        if current_width < 1000:
            # Mobile-friendly: stack elements
            top_row = ttk.Frame(search_inner)
            top_row.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(top_row, text="Search:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
            self.search_var = tk.StringVar()
            self.search_var.trace('w', lambda *args: self._on_search_change())
            ttk.Entry(top_row, textvariable=self.search_var, font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
            ttk.Button(top_row, text="X", width=3, command=lambda: self.search_var.set("")).pack(side=tk.LEFT, padx=5)
            
            bottom_row = ttk.Frame(search_inner)
            bottom_row.pack(fill=tk.X)
            ttk.Label(bottom_row, text="Filter:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
            self.filter_var = tk.StringVar(value="All")
            filter_combo = ttk.Combobox(bottom_row, textvariable=self.filter_var,
                                       values=["All", "VIP", "Potential"], state="readonly",
                                       font=('Segoe UI', 10))
            filter_combo.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
            filter_combo.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
            
            quick_frame = ttk.Frame(bottom_row)
            quick_frame.pack(side=tk.RIGHT, padx=(10, 0))
        else:
            # Desktop: horizontal layout
            ttk.Label(search_inner, text="Search:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
            self.search_var = tk.StringVar()
            self.search_var.trace('w', lambda *args: self._on_search_change())
            ttk.Entry(search_inner, textvariable=self.search_var, width=25,
                     font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(10, 5))
            ttk.Button(search_inner, text="X", width=3,
                      command=lambda: self.search_var.set("")).pack(side=tk.LEFT, padx=(0, 20))
            
            ttk.Label(search_inner, text="Filter:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
            self.filter_var = tk.StringVar(value="All")
            filter_combo = ttk.Combobox(search_inner, textvariable=self.filter_var,
                                       values=["All", "VIP", "Potential"], state="readonly",
                                       width=12, font=('Segoe UI', 10))
            filter_combo.pack(side=tk.LEFT, padx=10)
            filter_combo.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
            
            quick_frame = ttk.Frame(search_inner)
            quick_frame.pack(side=tk.RIGHT)
        ttk.Button(quick_frame, text="Add New", command=self._show_add_dialog,
                  style="Modern.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Export", command=self._export_to_excel).pack(side=tk.LEFT, padx=5)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Responsive layout: side-by-side on large screens, stacked on small screens
        current_width = self.root.winfo_width()
        is_small_screen = current_width < 1200
        
        table_card = tk.Frame(content_frame, bg=self.COLORS['card'],
                             highlightbackground=self.COLORS['border'], highlightthickness=1)
        if is_small_screen:
            table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        else:
            table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.table_card = table_card
        
        table_header = tk.Frame(table_card, bg=self.COLORS['card'])
        table_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        tk.Label(table_header, text="Customer List", font=('Segoe UI', 12, 'bold'),
                bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        
        table_frame = ttk.Frame(table_card)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columns = ("id", "name", "phone", "email", "type", "region", "interactions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                selectmode="browse", style="Custom.Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.heading("type", text="Type")
        self.tree.heading("region", text="Region")
        self.tree.heading("interactions", text="#")
        
        # Responsive column widths
        if current_width < 1000:
            self.tree.column("id", width=50, minwidth=40)
            self.tree.column("name", width=100, minwidth=80)
            self.tree.column("phone", width=90, minwidth=80)
            self.tree.column("email", width=120, minwidth=100)
            self.tree.column("type", width=60, minwidth=50)
            self.tree.column("region", width=80, minwidth=60)
            self.tree.column("interactions", width=35, minwidth=30)
        else:
            self.tree.column("id", width=70, minwidth=60)
            self.tree.column("name", width=140, minwidth=100)
            self.tree.column("phone", width=130, minwidth=100)
            self.tree.column("email", width=180, minwidth=120)
            self.tree.column("type", width=80, minwidth=70)
            self.tree.column("region", width=120, minwidth=80)
            self.tree.column("interactions", width=40, minwidth=35)
        
        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', lambda e: self._show_edit_dialog())
        self.tree.tag_configure('vip', background='#fef3c7')
        self.tree.tag_configure('potential', background='#dbeafe')
        
        action_frame = tk.Frame(table_card, bg=self.COLORS['card'])
        action_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Responsive button layout
        if current_width < 1000:
            # Stack buttons in two rows for small screens
            btn_row1 = ttk.Frame(action_frame)
            btn_row1.pack(fill=tk.X, pady=(0, 5))
            ttk.Button(btn_row1, text="Edit", command=self._show_edit_dialog).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
            ttk.Button(btn_row1, text="Delete", command=self._delete_customer).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            ttk.Button(btn_row1, text="View", command=self._show_interactions_dialog).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            btn_row2 = ttk.Frame(action_frame)
            btn_row2.pack(fill=tk.X)
            ttk.Button(btn_row2, text="Email", command=self._show_email_blast_dialog).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
            ttk.Button(btn_row2, text="Birthdays", command=self._check_birthdays).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        else:
            # Horizontal layout for large screens
            ttk.Button(action_frame, text="Edit", command=self._show_edit_dialog).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(action_frame, text="Delete", command=self._delete_customer).pack(side=tk.LEFT, padx=5)
            ttk.Button(action_frame, text="Interactions", command=self._show_interactions_dialog).pack(side=tk.LEFT, padx=5)
            ttk.Separator(action_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=15)
            ttk.Button(action_frame, text="Email Blast", command=self._show_email_blast_dialog).pack(side=tk.LEFT, padx=5)
            ttk.Button(action_frame, text="Birthdays", command=self._check_birthdays).pack(side=tk.LEFT, padx=5)
        
        chart_card = tk.Frame(content_frame, bg=self.COLORS['card'],
                             highlightbackground=self.COLORS['border'], highlightthickness=1)
        if is_small_screen:
            chart_card.pack(fill=tk.X)
            chart_card.pack_propagate(True)
        else:
            chart_card.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            chart_card.pack_propagate(False)
            chart_card.configure(width=420)
        
        chart_header = tk.Frame(chart_card, bg=self.COLORS['card'])
        chart_header.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(chart_header, text="Statistics", font=('Segoe UI', 12, 'bold'),
                bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        
        self.chart_frame = ChartFrame(chart_card, self.report_service)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _get_displayed_customers(self) -> List[Customer]:
        customers = self.crm_service.get_all_customers()
        
        if self.current_filter != "All":
            customers = [c for c in customers if c.customer_type == self.current_filter]
        
        if self.current_search:
            # Use fuzzy search on name, phone, and email
            customers = [c for c in customers
                        if (self._fuzzy_match(self.current_search, c.name, threshold=0.6) or
                            self._fuzzy_match(self.current_search, c.phone, threshold=0.7) or
                            self._fuzzy_match(self.current_search, c.email, threshold=0.6))]
        
        return customers
    
    def _refresh_table(self) -> None:
        self.crm_service.load_customers()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        customers = self._get_displayed_customers()
        
        for customer in customers:
            tag = 'vip' if customer.customer_type == 'VIP' else 'potential'
            region = customer.get_region()
            if len(region) > 15:
                region = region[:12] + '...'
            
            self.tree.insert("", tk.END, values=(
                customer.id, customer.name, customer.phone, customer.email,
                customer.customer_type, region, len(customer.interactions)
            ), tags=(tag,))
        
        total = len(self.crm_service.get_all_customers())
        displayed = len(customers)
        
        if total == displayed:
            self.count_label.config(text=f"{total} customers")
        else:
            self.count_label.config(text=f"{displayed} of {total} customers")
        
        self._update_chart()
    
    def _update_chart(self) -> None:
        type_stats = self.crm_service.get_customer_type_stats()
        region_stats = self.crm_service.get_region_stats()
        self.chart_frame.update_stats(type_stats, region_stats)
    
    def _get_selected_customer(self) -> Optional[Customer]:
        selected = self.tree.selection()
        if not selected:
            return None
        customer_id = self.tree.item(selected[0], "values")[0]
        return self.crm_service.get_customer(customer_id)
    
    def _on_search_change(self) -> None:
        """Handle search input with real-time filtering (efficient)."""
        self.current_search = self.search_var.get()
        # Only update the display, don't refresh data from service
        self._update_table_display()
    
    def _update_table_display(self) -> None:
        """Update table display with current filter and search (efficient - no data reload)."""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get displayed customers (already filtered by current_search)
        customers = self._get_displayed_customers()
        
        # Add to table
        for customer in customers:
            tag = 'vip' if customer.customer_type == 'VIP' else 'potential'
            region = customer.get_region()
            if len(region) > 15:
                region = region[:12] + '...'
            
            self.tree.insert("", tk.END, values=(
                customer.id, customer.name, customer.phone, customer.email,
                customer.customer_type, region, len(customer.interactions)
            ), tags=(tag,))
        
        # Update count
        total = len(self.crm_service.get_all_customers())
        displayed = len(customers)
        
        if total == displayed:
            self.count_label.config(text=f"{total} customers")
        else:
            self.count_label.config(text=f"{displayed} of {total} customers")
    
    def _on_filter_change(self) -> None:
        self.current_filter = self.filter_var.get()
        self._refresh_table()
    
    def _show_add_dialog(self) -> None:
        def on_save(data: dict):
            success, msg, _ = self.crm_service.add_customer(
                name=data['name'], phone=data['phone'], email=data['email'],
                customer_type=data['customer_type'], address=data['address'],
                date_of_birth=data['date_of_birth']
            )
            if success:
                messagebox.showinfo("Success", msg)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg)
        
        CustomerFormDialog(self.root, on_save=on_save)
    
    def _show_edit_dialog(self) -> None:
        customer = self._get_selected_customer()
        if not customer:
            messagebox.showwarning("No Selection", "Please select a customer to edit.")
            return
        
        def on_save(data: dict):
            success, msg = self.crm_service.update_customer(
                customer_id=data['id'], name=data['name'], phone=data['phone'],
                email=data['email'], customer_type=data['customer_type'],
                address=data['address'], date_of_birth=data['date_of_birth']
            )
            if success:
                messagebox.showinfo("Success", msg)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg)
        
        CustomerFormDialog(self.root, customer=customer, on_save=on_save)
    
    def _delete_customer(self) -> None:
        customer = self._get_selected_customer()
        if not customer:
            messagebox.showwarning("No Selection", "Please select a customer to delete.")
            return
        
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete '{customer.name}'?\n\nThis action cannot be undone."):
            return
        
        success, msg = self.crm_service.delete_customer(customer.id)
        if success:
            messagebox.showinfo("Success", msg)
            self._refresh_table()
        else:
            messagebox.showerror("Error", msg)
    
    def _show_interactions_dialog(self) -> None:
        customer = self._get_selected_customer()
        if not customer:
            messagebox.showwarning("No Selection", "Please select a customer to view interactions.")
            return
        
        def on_add(customer_id: str, date: str, content: str):
            self.crm_service.add_interaction(customer_id, date, content)
        
        def on_delete(customer_id: str, index: int):
            self.crm_service.delete_interaction(customer_id, index)
        
        InteractionFormDialog(self.root, customer=customer, on_add=on_add, on_delete=on_delete)
        self._refresh_table()
    
    def _check_birthdays(self) -> None:
        birthday_customers = self.crm_service.check_birthdays()
        
        if not birthday_customers:
            messagebox.showinfo("Birthday Check", "No customers have birthdays today.")
            return
        
        names = [f"- {c.name}" for c in birthday_customers]
        messagebox.showinfo("Birthday Alert!",
                           f"The following customers have birthdays today:\n\n" + "\n".join(names) +
                           "\n\nConsider sending them birthday wishes!")
    
    def _show_email_blast_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Email Blast")
        dialog.geometry("320x220")
        dialog.configure(bg=self.COLORS['card'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 160
        y = (dialog.winfo_screenheight() // 2) - 110
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Email Blast", font=('Segoe UI', 14, 'bold'),
                bg=self.COLORS['card'], fg=self.COLORS['text']).pack(pady=20)
        tk.Label(dialog, text="Select target group:", font=('Segoe UI', 10),
                bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack()
        
        target_var = tk.StringVar(value="All")
        for target, val in [("All Customers", "All"), ("VIP Only", "VIP"), ("Potential Only", "Potential")]:
            ttk.Radiobutton(dialog, text=target, variable=target_var, value=val).pack(anchor=tk.W, padx=50, pady=2)
        
        def send():
            self._email_blast(target_var.get())
            dialog.destroy()
        
        ttk.Button(dialog, text="Send Blast", command=send, style="Modern.TButton").pack(pady=20)
    
    def _email_blast(self, target: str) -> None:
        """Send real bulk emails to customers."""
        from services.email_templates import TEMPLATES
        
        # Check if email is configured
        if not self.email_service.config.is_configured():
            messagebox.showwarning(
                "Email Not Configured",
                "Please configure email settings first.\n\n" +
                "Go to Marketing → Email Settings"
            )
            return
        
        # Get target customers
        count, emails = self.crm_service.simulate_email_blast(target)
        
        if count == 0:
            messagebox.showinfo("Email Blast", f"No {target} customers to send emails to.")
            return
        
        # Confirm before sending
        preview = "\n".join([f"- {e}" for e in emails[:5]])
        if count > 5:
            preview += f"\n- ... and {count - 5} more"
        
        confirm = messagebox.askyesno(
            "Confirm Email Blast",
            f"Send emails to {count} {target} customers?\n\n" +
            f"Recipients:\n{preview}\n\n" +
            "⚠️ This will send REAL emails!"
        )
        
        if not confirm:
            return
        
        # Get template
        template = TEMPLATES.get('promotional')
        subject = template.subject
        body = template.body
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Sending Emails...")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.transient(self.root)
        
        ttk.Label(progress_window, text=f"Sending emails to {count} customers...",
                 font=('Segoe UI', 10, 'bold')).pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, length=350, mode='determinate',
                                       maximum=count)
        progress_bar.pack(pady=10, padx=25)
        
        status_label = ttk.Label(progress_window, text="0 / " + str(count),
                                font=('Segoe UI', 9))
        status_label.pack(pady=5)
        
        # Send emails
        success_count = 0
        fail_count = 0
        errors = []
        
        for idx, email in enumerate(emails):
            try:
                success, msg = self.email_service.send_email(
                    email, subject, body, None
                )
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    errors.append(f"{email}: {msg}")
            except Exception as e:
                fail_count += 1
                errors.append(f"{email}: {str(e)}")
            
            # Update progress
            progress_bar['value'] = idx + 1
            status_label.config(text=f"{idx + 1} / {count}")
            progress_window.update()
            
            # Small delay to avoid overwhelming SMTP server
            self.root.after(100)
        
        progress_window.destroy()
        
        # Show results
        if fail_count == 0:
            messagebox.showinfo(
                "✅ Email Blast Sent!",
                f"Successfully sent {success_count} emails to {target} customers!"
            )
        else:
            error_preview = "\n".join(errors[:5])
            if len(errors) > 5:
                error_preview += f"\n... and {len(errors) - 5} more errors"
            
            messagebox.showwarning(
                "⚠️ Email Blast Completed",
                f"Sent: {success_count} / Failed: {fail_count}\n\n" +
                f"Errors:\n{error_preview}"
            )
    
    def _export_to_excel(self) -> None:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export to Excel"
        )
        
        if not filepath:
            return
        
        customers = self._get_displayed_customers()
        if not customers:
            messagebox.showwarning("No Data", "No customers to export.")
            return
        
        success, result = self.report_service.export_to_excel(customers, filename=os.path.basename(filepath))
        
        if success:
            messagebox.showinfo("Export Successful", f"Exported {len(customers)} customers to:\n{result}")
        else:
            messagebox.showerror("Export Failed", result)
    
    def _show_about(self) -> None:
        messagebox.showinfo("About Mini CRM",
                           "Mini CRM v1.0\n\n"
                           "Customer Relationship Management System\n"
                           "Topic 20: University Group Project\n\n"
                           "Features:\n"
                           "- Customer CRUD operations\n"
                           "- Search & Filter\n"
                           "- Birthday reminders\n"
                           "- Email blast simulation\n"
                           "- Excel export with pandas\n"
                           "- Interactive charts with matplotlib\n\n"
                           "Built with Python, Tkinter, pandas & matplotlib")
    
    def _on_window_resize(self, event=None) -> None:
        """Handle window resize to adjust layout responsively."""
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Only redraw if size change is significant
        if abs(current_width - self.last_width) > 100 or abs(current_height - self.last_height) > 100:
            self.last_width = current_width
            self.last_height = current_height
            
            # Adjust layout based on screen size
            is_small_screen = current_width < 1200
            if is_small_screen != self.is_responsive_mode:
                self.is_responsive_mode = is_small_screen
                # Clear main content and recreate widgets for responsive layout
                for widget in self.root.winfo_children():
                    if isinstance(widget, (ttk.Frame, tk.Frame)):
                        widget.destroy()
                self._create_widgets()
                self._refresh_table()
                self._update_chart()
    
    def _send_email_to_selected(self) -> None:
        """Open email dialog to send email to selected customer."""
        customer = self._get_selected_customer()
        if not customer:
            messagebox.showwarning("No Selection", "Please select a customer to send email to.")
            return
        
        def on_send_callback():
            # Add interaction to customer record
            self.crm_service.add_interaction(customer.id, datetime.now().strftime("%Y-%m-%d"), 
                                             f"Received email: [automated message]")
            self._refresh_table()
        
        EmailDialog(self.root, customer, on_send_callback)
    
    def _show_email_settings(self) -> None:
        """Open email settings dialog."""
        EmailSettingsDialog(self.root)
    
    def _show_email_log(self) -> None:
        """Show email log window."""
        email_service = EmailService()
        log = email_service.get_email_log(100)
        
        if not log:
            messagebox.showinfo("Email Log", "No emails have been sent yet.")
            return
        
        # Create log window
        log_window = tk.Toplevel(self.root)
        log_window.title("Email Log")
        log_window.geometry("700x500")
        log_window.transient(self.root)
        
        # Create treeview
        columns = ("Timestamp", "Recipient", "Subject")
        tree = ttk.Treeview(log_window, columns=columns, height=20)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("Timestamp", anchor=tk.W, width=150)
        tree.column("Recipient", anchor=tk.W, width=200)
        tree.column("Subject", anchor=tk.W, width=350)
        
        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("Timestamp", text="Timestamp", anchor=tk.W)
        tree.heading("Recipient", text="Recipient", anchor=tk.W)
        tree.heading("Subject", text="Subject", anchor=tk.W)
        
        # Add data
        for item in log:
            timestamp = item.get("timestamp", "").split("T")[0] + " " + item.get("timestamp", "").split("T")[1][:5] if "T" in item.get("timestamp", "") else item.get("timestamp", "")
            recipient = item.get("recipient_name", "")
            subject = item.get("subject", "")
            tree.insert("", tk.END, values=(timestamp, recipient, subject))
    

    def _on_closing(self) -> None:
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def run(self) -> None:
        self.root.mainloop()
