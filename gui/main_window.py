"""Main application window for the Mini CRM system."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
import os

from models.customer import Customer
from services.crm_service import CRMService
from services.report_service import ReportService
from services.data_service import DataService
from gui.customer_form import CustomerFormDialog
from gui.interaction_form import InteractionFormDialog
from gui.chart_frame import ChartFrame


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
        self.root.geometry("1280x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg=self.COLORS['bg'])
        
        self.data_service = DataService()
        self.crm_service = CRMService(self.data_service)
        self.report_service = ReportService()
        
        self.current_filter = "All"
        self.current_search = ""
        
        self._apply_theme()
        self._create_menu()
        self._create_widgets()
        self._refresh_table()
        self._update_chart()
        self._check_birthdays()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _apply_theme(self) -> None:
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        style.configure("TFrame", background=self.COLORS['bg'])
        style.configure("TLabel", background=self.COLORS['bg'], foreground=self.COLORS['text'], font=('Segoe UI', 10))
        style.configure("Title.TLabel", font=('Segoe UI', 20, 'bold'), foreground=self.COLORS['text'])
        style.configure("Subtitle.TLabel", font=('Segoe UI', 12), foreground=self.COLORS['text_muted'])
        
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
        marketing_menu.add_command(label="Email Blast - All", command=lambda: self._email_blast("All"))
        marketing_menu.add_command(label="Email Blast - VIP", command=lambda: self._email_blast("VIP"))
        marketing_menu.add_command(label="Email Blast - Potential", command=lambda: self._email_blast("Potential"))
        marketing_menu.add_separator()
        marketing_menu.add_command(label="Check Birthdays", command=self._check_birthdays)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Mini CRM Dashboard", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(title_frame, text="Manage your customer relationships effectively",
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side=tk.RIGHT)
        self.count_label = ttk.Label(stats_frame, text="25 customers",
                                     font=('Segoe UI', 14, 'bold'), foreground=self.COLORS['primary'])
        self.count_label.pack(side=tk.RIGHT)
        
        search_card = tk.Frame(main_frame, bg=self.COLORS['card'],
                              highlightbackground=self.COLORS['border'], highlightthickness=1)
        search_card.pack(fill=tk.X, pady=(0, 15))
        
        search_inner = ttk.Frame(search_card)
        search_inner.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(search_inner, text="Search:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._on_search_change())
        ttk.Entry(search_inner, textvariable=self.search_var, width=35,
                 font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(search_inner, text="X", width=3,
                  command=lambda: self.search_var.set("")).pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(search_inner, text="Filter:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(search_inner, textvariable=self.filter_var,
                                   values=["All", "VIP", "Potential"], state="readonly",
                                   width=15, font=('Segoe UI', 10))
        filter_combo.pack(side=tk.LEFT, padx=10)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
        
        quick_frame = ttk.Frame(search_inner)
        quick_frame.pack(side=tk.RIGHT)
        ttk.Button(quick_frame, text="Add New", command=self._show_add_dialog,
                  style="Modern.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Export", command=self._export_to_excel).pack(side=tk.LEFT, padx=5)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        table_card = tk.Frame(content_frame, bg=self.COLORS['card'],
                             highlightbackground=self.COLORS['border'], highlightthickness=1)
        table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
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
        
        ttk.Button(action_frame, text="Edit", command=self._show_edit_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Delete", command=self._delete_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Interactions", command=self._show_interactions_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Separator(action_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=15)
        ttk.Button(action_frame, text="Email Blast", command=self._show_email_blast_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Birthdays", command=self._check_birthdays).pack(side=tk.LEFT, padx=5)
        
        chart_card = tk.Frame(content_frame, bg=self.COLORS['card'],
                             highlightbackground=self.COLORS['border'], highlightthickness=1, width=420)
        chart_card.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        chart_card.pack_propagate(False)
        
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
            query = self.current_search.lower()
            customers = [c for c in customers
                        if query in c.name.lower() or query in c.phone or query in c.email.lower()]
        
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
        self.current_search = self.search_var.get()
        self._refresh_table()
    
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
        count, emails = self.crm_service.simulate_email_blast(target)
        
        if count == 0:
            messagebox.showinfo("Email Blast", f"No {target} customers to send emails to.")
            return
        
        preview = "\n".join([f"- {e}" for e in emails[:5]])
        if count > 5:
            preview += f"\n- ... and {count - 5} more"
        
        messagebox.showinfo("Email Blast Sent!",
                           f"Email blast simulated successfully!\n\n"
                           f"Target: {target}\nRecipients: {count}\n\n"
                           f"Sample:\n{preview}\n\n(Simulation only - no real emails sent)")
    
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
    
    def _on_closing(self) -> None:
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def run(self) -> None:
        self.root.mainloop()
