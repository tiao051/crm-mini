"""Email sending dialog for the CRM GUI."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from models.customer import Customer
from services.email_service import EmailService
from services.email_templates import get_template_ids, get_template, TEMPLATES


class EmailDialog:
    """Dialog for composing and sending emails to a customer."""
    
    def __init__(self, parent, customer: Customer, on_send_callback: Optional[Callable] = None):
        """
        Create email dialog.
        
        Args:
            parent: Parent window
            customer: Customer to send email to
            on_send_callback: Optional callback when email is sent
        """
        self.parent = parent
        self.customer = customer
        self.on_send_callback = on_send_callback
        self.email_service = EmailService()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Send Email - {customer.name}")
        self.dialog.geometry("700x600")
        self.dialog.minsize(600, 500)
        self.dialog.resizable(True, True)
        
        # Center on parent
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Colors
        bg_color = '#f0f2f5'
        card_color = '#ffffff'
        
        self.dialog.configure(bg=bg_color)
        
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # --- Recipient Info ---
        recipient_frame = ttk.LabelFrame(main_frame, text="Recipient", padding=10)
        recipient_frame.pack(fill=tk.X, pady=(0, 12))
        
        ttk.Label(recipient_frame, text=f"Name: {self.customer.name}").pack(anchor=tk.W)
        ttk.Label(recipient_frame, text=f"Email: {self.customer.email}").pack(anchor=tk.W)
        
        # --- Template Selection ---
        template_frame = ttk.LabelFrame(main_frame, text="Email Template", padding=10)
        template_frame.pack(fill=tk.X, pady=(0, 12))
        
        template_ids = get_template_ids()
        template_names = [TEMPLATES[tid].name for tid in template_ids]
        
        ttk.Label(template_frame, text="Choose template:").pack(anchor=tk.W, pady=(0, 5))
        
        self.template_combo = ttk.Combobox(
            template_frame,
            values=template_names,
            state='readonly',
            width=40
        )
        self.template_combo.set(template_names[0])
        self.template_combo.pack(anchor=tk.W, fill=tk.X)
        self.template_combo.bind('<<ComboboxSelected>>', self._on_template_changed)
        
        # --- Subject ---
        subject_frame = ttk.LabelFrame(main_frame, text="Subject", padding=10)
        subject_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.subject_entry = ttk.Entry(subject_frame, width=60)
        self.subject_entry.pack(fill=tk.X)
        
        # --- Body ---
        body_frame = ttk.LabelFrame(main_frame, text="Message Body", padding=10)
        body_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(body_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.body_text = tk.Text(
            body_frame,
            height=15,
            width=60,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD
        )
        self.body_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.body_text.yview)
        
        # --- Variables hint ---
        hint_text = "Available variables: {customer_name}, {email}, {phone}, {customer_type}, {address}"
        ttk.Label(main_frame, text=hint_text, font=("Arial", 8), foreground="#6b7280").pack(
            anchor=tk.W, pady=(0, 12)
        )
        
        # --- Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Send Email", command=self._send_email).pack(side=tk.RIGHT)
        
        # Load initial template
        self._on_template_changed()
    
    def _on_template_changed(self, event=None):
        """Handle template selection change."""
        selected_name = self.template_combo.get()
        
        # Find template ID by name
        template_id = None
        for tid, template in TEMPLATES.items():
            if template.name == selected_name:
                template_id = tid
                break
        
        if not template_id:
            return
        
        template = get_template(template_id)
        
        # Prepare template variables
        variables = {
            'customer_name': self.customer.name,
            'email': self.customer.email,
            'phone': self.customer.phone,
            'customer_type': self.customer.customer_type,
            'address': self.customer.address
        }
        
        # Render template
        subject, body = template.render(**variables)
        
        # Update fields
        self.subject_entry.delete(0, tk.END)
        self.subject_entry.insert(0, subject)
        
        self.body_text.delete('1.0', tk.END)
        self.body_text.insert('1.0', body)
    
    def _send_email(self):
        """Send the email."""
        subject = self.subject_entry.get().strip()
        body = self.body_text.get('1.0', tk.END).strip()
        
        # Validation
        if not subject:
            messagebox.showerror("Validation Error", "Please enter a subject")
            return
        
        if not body:
            messagebox.showerror("Validation Error", "Please enter a message body")
            return
        
        # Send
        success, message = self.email_service.send_email(
            self.customer.email,
            subject,
            body,
            self.customer.name
        )
        
        if success:
            messagebox.showinfo("Success", message)
            
            # Call callback if provided
            if self.on_send_callback:
                self.on_send_callback()
            
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", message)


class EmailSettingsDialog:
    """Dialog for configuring email settings."""
    
    def __init__(self, parent):
        """Create email settings dialog."""
        self.parent = parent
        self.email_service = EmailService()
        self.config = self.email_service.config
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Email Settings")
        self.dialog.geometry("600x400")
        self.dialog.resizable(False, False)
        
        # Center on parent
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        bg_color = '#f0f2f5'
        self.dialog.configure(bg=bg_color)
        
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(
            main_frame,
            text="Email Configuration (SMTP)",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # SMTP Server
        ttk.Label(main_frame, text="SMTP Server:").pack(anchor=tk.W)
        self.server_entry = ttk.Entry(main_frame, width=50)
        self.server_entry.pack(fill=tk.X, pady=(0, 12))
        self.server_entry.insert(0, self.config.settings.get("smtp_server", "smtp.gmail.com"))
        
        # SMTP Port
        ttk.Label(main_frame, text="SMTP Port:").pack(anchor=tk.W)
        self.port_entry = ttk.Entry(main_frame, width=50)
        self.port_entry.pack(fill=tk.X, pady=(0, 12))
        self.port_entry.insert(0, str(self.config.settings.get("smtp_port", 587)))
        
        # Sender Email
        ttk.Label(main_frame, text="Sender Email Address:").pack(anchor=tk.W)
        self.email_entry = ttk.Entry(main_frame, width=50)
        self.email_entry.pack(fill=tk.X, pady=(0, 12))
        self.email_entry.insert(0, self.config.settings.get("sender_email", ""))
        
        # Sender Password/App Password
        ttk.Label(main_frame, text="Password (App Password for Gmail):").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(main_frame, width=50, show="•")
        self.password_entry.pack(fill=tk.X, pady=(0, 12))
        
        # Sender Name
        ttk.Label(main_frame, text="Sender Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill=tk.X, pady=(0, 20))
        self.name_entry.insert(0, self.config.settings.get("sender_name", "CRM System"))
        
        # Info text
        info_text = ttk.Label(
            main_frame,
            text="💡 For Gmail: Use App Password (Generate from Security Settings)",
            font=("Arial", 9),
            foreground="#6b7280"
        )
        info_text.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Test Connection", command=self._test_connection).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save Settings", command=self._save_settings).pack(side=tk.RIGHT)
    
    def _test_connection(self):
        """Test SMTP connection."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        server = self.server_entry.get().strip()
        
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        try:
            with smtplib.SMTP(server, port, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(email, password)
            messagebox.showinfo("Success", "Connection test passed!")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
    
    def _save_settings(self):
        """Save email settings."""
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        settings = {
            "smtp_server": self.server_entry.get().strip(),
            "smtp_port": port,
            "sender_email": self.email_entry.get().strip(),
            "sender_password": self.password_entry.get().strip(),
            "sender_name": self.name_entry.get().strip()
        }
        
        if not settings["sender_email"] or not settings["sender_password"]:
            messagebox.showerror("Error", "Email and password are required")
            return
        
        self.config.settings = settings
        if self.config.save_config(settings):
            messagebox.showinfo("Success", "Email settings saved!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")


import smtplib  # Import at top for _test_connection method
