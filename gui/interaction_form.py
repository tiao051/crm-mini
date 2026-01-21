"""
Dialog window for managing customer interaction history.
Allows viewing, adding, and deleting interactions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from datetime import datetime

from models.customer import Customer
from models.interaction import Interaction


class InteractionFormDialog(tk.Toplevel):
    """Modal dialog for managing customer interactions."""
    
    def __init__(
        self,
        parent: tk.Widget,
        customer: Customer,
        on_add: Optional[Callable[[str, str, str], None]] = None,
        on_delete: Optional[Callable[[str, int], None]] = None
    ):
        """Initialize the Interaction Form Dialog."""
        super().__init__(parent)
        
        self.customer = customer
        self.on_add = on_add
        self.on_delete = on_delete
        
        self.title(f"Interactions - {customer.name}")
        # Fixed dialog size - compact and clean
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set fixed but reasonable size
        dialog_width = 550
        dialog_height = 580
        
        # Center on screen
        x = (screen_width - dialog_width) // 2
        y = max(50, (screen_height - dialog_height) // 2)
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.minsize(500, 550)
        self.resizable(True, True)
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_interactions()
    
    def _create_widgets(self) -> None:
        """Create and layout form widgets."""
        
        dialog_width = self.winfo_width() if self.winfo_width() > 1 else 600
        
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_size = 11 if dialog_width < 500 else 12
        title_label = ttk.Label(
            main_frame,
            text=f"📋 Interaction History for {self.customer.name}",
            font=('Segoe UI', title_size, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        list_frame = ttk.LabelFrame(main_frame, text="Interactions", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for interactions
        columns = ("date", "content")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        self.tree.heading("date", text="Date")
        self.tree.heading("content", text="Content")
        
        # Responsive column widths
        if dialog_width < 500:
            self.tree.column("date", width=70, minwidth=60)
            self.tree.column("content", width=250, minwidth=150)
        else:
            self.tree.column("date", width=100, minwidth=80)
            self.tree.column("content", width=400, minwidth=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        delete_btn = ttk.Button(
            main_frame,
            text="🗑️ Delete Selected",
            command=self._on_delete
        )
        delete_btn.pack(pady=(10, 0), anchor=tk.E)
        
        add_frame = ttk.LabelFrame(main_frame, text="Add New Interaction", padding=10)
        add_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Responsive layout for date field
        if dialog_width < 500:
            # Stacked layout for small screens
            date_row = ttk.Frame(add_frame)
            date_row.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(date_row, text="Date:").pack(anchor=tk.W)
            
            today = datetime.now().strftime("%Y-%m-%d")
            self.date_var = tk.StringVar(value=today)
            date_entry_row = ttk.Frame(add_frame)
            date_entry_row.pack(fill=tk.X, pady=(0, 10))
            
            self.date_entry = ttk.Entry(date_entry_row, textvariable=self.date_var)
            self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            today_btn = ttk.Button(
                date_entry_row,
                text="Today",
                command=lambda: self.date_var.set(datetime.now().strftime("%Y-%m-%d")),
                width=6
            )
            today_btn.pack(side=tk.LEFT)
        else:
            # Horizontal layout for large screens
            date_row = ttk.Frame(add_frame)
            date_row.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(date_row, text="Date:").pack(side=tk.LEFT)
            
            today = datetime.now().strftime("%Y-%m-%d")
            self.date_var = tk.StringVar(value=today)
            self.date_entry = ttk.Entry(date_row, textvariable=self.date_var, width=15)
            self.date_entry.pack(side=tk.LEFT, padx=(10, 0))
            
            ttk.Label(date_row, text="(YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=(5, 0))
            
            today_btn = ttk.Button(
                date_row,
                text="Today",
                command=lambda: self.date_var.set(datetime.now().strftime("%Y-%m-%d")),
                width=8
            )
            today_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        content_row = ttk.Frame(add_frame)
        content_row.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(content_row, text="Content:").pack(side=tk.LEFT, anchor=tk.N)
        
        text_height = 2 if dialog_width < 500 else 3
        self.content_text = tk.Text(content_row, height=text_height, wrap=tk.WORD)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        add_btn = ttk.Button(
            add_frame,
            text="➕ Add Interaction",
            command=self._on_add
        )
        add_btn.pack(pady=(5, 0), anchor=tk.E)
        
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.destroy,
            width=15
        )
        close_btn.pack(pady=(15, 0))
        
        # Bind Escape to close
        self.bind('<Escape>', lambda e: self.destroy())
    
    def _load_interactions(self) -> None:
        """Load interactions into the treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sort interactions by date (newest first)
        sorted_interactions = sorted(
            enumerate(self.customer.interactions),
            key=lambda x: x[1].date,
            reverse=True
        )
        
        # Add to treeview
        for original_index, interaction in sorted_interactions:
            self.tree.insert(
                "",
                tk.END,
                values=(interaction.date, interaction.content),
                tags=(str(original_index),)  # Store original index for deletion
            )
        
        # Update title with count
        count = len(self.customer.interactions)
        self.title(f"Interactions - {self.customer.name} ({count} total)")
    
    def _on_add(self) -> None:
        """Handle add interaction button click."""
        date = self.date_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        # Validate date
        if not date:
            messagebox.showwarning("Validation Error", "Please enter a date.")
            return
        
        # Simple date format check
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Invalid date format. Use YYYY-MM-DD."
            )
            return
        
        # Validate content
        if not content:
            messagebox.showwarning("Validation Error", "Please enter interaction content.")
            return
        
        # Call callback
        if self.on_add:
            self.on_add(self.customer.id, date, content)
            
            # Add to local list for immediate display
            self.customer.add_interaction(date, content)
            
            # Refresh list
            self._load_interactions()
            
            # Clear form
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
            self.content_text.delete("1.0", tk.END)
            
            messagebox.showinfo("Success", "Interaction added successfully!")
    
    def _on_delete(self) -> None:
        """Handle delete interaction button click."""
        # Get selected item
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select an interaction to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this interaction?"
        ):
            return
        
        # Get original index from tags
        item = selected[0]
        tags = self.tree.item(item, "tags")
        
        if tags:
            original_index = int(tags[0])
            
            # Call callback
            if self.on_delete:
                self.on_delete(self.customer.id, original_index)
            
            # Remove from local list
            if 0 <= original_index < len(self.customer.interactions):
                self.customer.interactions.pop(original_index)
            
            # Refresh list
            self._load_interactions()
            
            messagebox.showinfo("Success", "Interaction deleted successfully!")
