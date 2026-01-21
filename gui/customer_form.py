"""
Modern dialog window for adding and editing customer information.
Clean design with proper validation feedback.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Tuple
from datetime import datetime

from models.customer import Customer
from services.validation import (
    validate_name,
    validate_phone,
    validate_email,
    validate_date,
    validate_customer_type
)


class CustomerFormDialog(tk.Toplevel):
    """
    Modern modal dialog for adding or editing customer information.
    """
    
    COLORS = {
        'bg': '#ffffff',
        'text': '#1f2937',
        'text_muted': '#6b7280',
        'primary': '#6366f1',
        'border': '#e5e7eb',
        'error': '#ef4444',
        'success': '#10b981',
    }
    
    def __init__(
        self,
        parent: tk.Widget,
        customer: Optional[Customer] = None,
        on_save: Optional[Callable[[dict], None]] = None
    ):
        super().__init__(parent)
        
        self.customer = customer
        self.on_save = on_save
        self.result = None
        
        self.title("➕ Add Customer" if customer is None else "✏️ Edit Customer")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(bg=self.COLORS['bg'])
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._create_widgets()
        
        if customer:
            self._populate_fields()
    
    def _center_window(self) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 260
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self) -> None:
        main_frame = tk.Frame(self, bg=self.COLORS['bg'], padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_text = "Add New Customer" if self.customer is None else "Edit Customer"
        tk.Label(
            main_frame,
            text=title_text,
            font=('Segoe UI', 16, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        ).pack(anchor=tk.W, pady=(0, 20))
        
        self._create_field(main_frame, "Full Name *", "name")
        self._create_field(main_frame, "Phone Number *", "phone")
        self._create_field(main_frame, "Email Address *", "email")
        self._create_type_field(main_frame)
        self._create_field(main_frame, "Address", "address")
        self._create_date_field(main_frame)
        
        # Error label
        self.error_label = tk.Label(
            main_frame,
            text="",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg'],
            fg=self.COLORS['error'],
            wraplength=400,
            justify=tk.LEFT
        )
        self.error_label.pack(anchor=tk.W, pady=(15, 0))
        
        btn_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            btn_frame,
            text="* Required fields",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_muted']
        ).pack(side=tk.LEFT)
        
        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Customer",
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground='#4f46e5',
            activeforeground='white',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self._on_save
        )
        save_btn.pack(side=tk.RIGHT)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=('Segoe UI', 10),
            bg='#f3f4f6',
            fg=self.COLORS['text'],
            activebackground='#e5e7eb',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        self.name_entry.focus_set()
        
        self.bind('<Return>', lambda e: self._on_save())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def _create_field(self, parent, label: str, field_name: str) -> None:
        """Create a modern input field."""
        frame = tk.Frame(parent, bg=self.COLORS['bg'])
        frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            frame,
            text=label,
            font=('Segoe UI', 10),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_muted']
        ).pack(anchor=tk.W)
        
        var = tk.StringVar()
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=('Segoe UI', 11),
            bg='#f9fafb',
            fg=self.COLORS['text'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.COLORS['primary'],
            highlightbackground=self.COLORS['border']
        )
        entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        setattr(self, f"{field_name}_var", var)
        setattr(self, f"{field_name}_entry", entry)
    
    def _create_type_field(self, parent) -> None:
        """Create customer type dropdown."""
        frame = tk.Frame(parent, bg=self.COLORS['bg'])
        frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            frame,
            text="Customer Type *",
            font=('Segoe UI', 10),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_muted']
        ).pack(anchor=tk.W)
        
        self.type_var = tk.StringVar(value="Potential")
        
        type_frame = tk.Frame(frame, bg=self.COLORS['bg'])
        type_frame.pack(fill=tk.X, pady=(5, 0))
        
        vip_frame = tk.Frame(type_frame, bg='#fef3c7', padx=15, pady=8)
        vip_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            vip_frame,
            text="⭐ VIP",
            variable=self.type_var,
            value="VIP"
        ).pack()
        
        pot_frame = tk.Frame(type_frame, bg='#dbeafe', padx=15, pady=8)
        pot_frame.pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            pot_frame,
            text="🎯 Potential",
            variable=self.type_var,
            value="Potential"
        ).pack()
    
    def _create_date_field(self, parent) -> None:
        """Create date of birth field with dropdowns."""
        frame = tk.Frame(parent, bg=self.COLORS['bg'])
        frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            frame,
            text="Date of Birth *",
            font=('Segoe UI', 10),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_muted']
        ).pack(anchor=tk.W)
        
        date_frame = tk.Frame(frame, bg=self.COLORS['bg'])
        date_frame.pack(fill=tk.X, pady=(5, 0))
        
        current_year = datetime.now().year
        years = list(range(current_year - 100, current_year - 17))[::-1]
        self.year_var = tk.StringVar(value=str(current_year - 30))
        year_combo = ttk.Combobox(
            date_frame,
            textvariable=self.year_var,
            values=years,
            width=8,
            state="readonly",
            font=('Segoe UI', 10)
        )
        year_combo.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text=" - ", bg=self.COLORS['bg'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        
        months = [f"{i:02d}" for i in range(1, 13)]
        self.month_var = tk.StringVar(value="06")
        month_combo = ttk.Combobox(
            date_frame,
            textvariable=self.month_var,
            values=months,
            width=5,
            state="readonly",
            font=('Segoe UI', 10)
        )
        month_combo.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text=" - ", bg=self.COLORS['bg'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        
        days = [f"{i:02d}" for i in range(1, 32)]
        self.day_var = tk.StringVar(value="15")
        day_combo = ttk.Combobox(
            date_frame,
            textvariable=self.day_var,
            values=days,
            width=5,
            state="readonly",
            font=('Segoe UI', 10)
        )
        day_combo.pack(side=tk.LEFT)
        
        tk.Label(
            date_frame,
            text="  (YYYY-MM-DD)",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_muted']
        ).pack(side=tk.LEFT)
    
    def _populate_fields(self) -> None:
        """Populate form with existing customer data."""
        if not self.customer:
            return
        
        self.name_var.set(self.customer.name)
        self.phone_var.set(self.customer.phone)
        self.email_var.set(self.customer.email)
        self.type_var.set(self.customer.customer_type)
        self.address_var.set(self.customer.address)
        
        if self.customer.date_of_birth:
            try:
                parts = self.customer.date_of_birth.split("-")
                if len(parts) == 3:
                    self.year_var.set(parts[0])
                    self.month_var.set(parts[1])
                    self.day_var.set(parts[2])
            except:
                pass
    
    def _get_date_of_birth(self) -> str:
        return f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
    
    def _validate_all(self) -> Tuple[bool, str]:
        is_valid, error = validate_name(self.name_var.get())
        if not is_valid:
            return False, f"Name: {error}"
        
        is_valid, error = validate_phone(self.phone_var.get())
        if not is_valid:
            return False, f"Phone: {error}"
        
        is_valid, error = validate_email(self.email_var.get())
        if not is_valid:
            return False, f"Email: {error}"
        
        is_valid, error = validate_customer_type(self.type_var.get())
        if not is_valid:
            return False, f"Type: {error}"
        
        is_valid, error = validate_date(self._get_date_of_birth())
        if not is_valid:
            return False, f"Birth Date: {error}"
        
        return True, ""
    
    def _on_save(self) -> None:
        self.error_label.config(text="")
        
        is_valid, error_msg = self._validate_all()
        
        if not is_valid:
            self.error_label.config(text=f"❌ {error_msg}")
            return
        
        form_data = {
            "name": self.name_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "email": self.email_var.get().strip(),
            "customer_type": self.type_var.get(),
            "address": self.address_var.get().strip(),
            "date_of_birth": self._get_date_of_birth()
        }
        
        if self.customer:
            form_data["id"] = self.customer.id
        
        self.result = form_data
        
        if self.on_save:
            self.on_save(form_data)
        
        self.destroy()
    
    def get_result(self) -> Optional[dict]:
        return self.result
