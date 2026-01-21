"""Report Service - Excel export and chart generation using pandas and matplotlib."""

import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from models.customer import Customer


class ReportService:
    """Service for generating reports and visualizations (Excel export, charts)."""
    
    DEFAULT_EXPORT_DIR = "./exports"
    
    def __init__(self, export_dir: Optional[str] = None):
        """Initialize with optional custom export directory."""
        self.export_dir = export_dir or self.DEFAULT_EXPORT_DIR
        self._ensure_export_directory()
    
    def _ensure_export_directory(self) -> None:
        """Create export directory if it doesn't exist."""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            print(f"Created export directory: {self.export_dir}")
    
    def export_to_excel(
        self,
        customers: List[Customer],
        filename: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Export customer data to Excel file with formatted columns."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"customers_export_{timestamp}.xlsx"
            
            filepath = os.path.join(self.export_dir, filename)
            data = []
            for customer in customers:
                last_interaction = ""
                if customer.interactions:
                    sorted_interactions = sorted(
                        customer.interactions,
                        key=lambda x: x.date,
                        reverse=True
                    )
                    last_interaction = sorted_interactions[0].date
                
                row = {
                    "Customer ID": customer.id,
                    "Name": customer.name,
                    "Phone": customer.phone,
                    "Email": customer.email,
                    "Customer Type": customer.customer_type,
                    "Address": customer.address,
                    "Date of Birth": customer.date_of_birth,
                    "Region": customer.get_region(),
                    "Total Interactions": len(customer.interactions),
                    "Last Interaction": last_interaction
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            df.to_excel(
                filepath,
                index=False,
                engine='openpyxl',
                sheet_name='Customers'
            )
            
            print(f"Successfully exported {len(customers)} customers to {filepath}")
            return True, filepath
            
        except PermissionError:
            error_msg = f"Permission denied. Cannot write to {filepath}"
            print(f"Error: {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error exporting to Excel: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def create_customer_type_chart(
        self,
        stats: Dict[str, int],
        chart_type: str = "pie"
    ) -> Figure:
        """Create pie or bar chart showing customer type distribution."""
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        labels = list(stats.keys())
        values = list(stats.values())
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0']
        
        if sum(values) == 0:
            ax.text(
                0.5, 0.5,
                "No customer data available",
                ha='center', va='center',
                transform=ax.transAxes,
                fontsize=12
            )
            ax.axis('off')
            return fig
        
        if chart_type.lower() == "pie":
            explode = [0.02] * len(values)
            
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(labels)],
                explode=explode,
                shadow=True
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title("Customer Type Distribution", fontsize=12, fontweight='bold')
            
        else:
            bars = ax.bar(
                labels,
                values,
                color=colors[:len(labels)],
                edgecolor='white',
                linewidth=1.2
            )
            
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.annotate(
                    f'{value}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontweight='bold'
                )
            
            ax.set_ylabel("Number of Customers")
            ax.set_title("Customer Type Distribution", fontsize=12, fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        fig.tight_layout()
        return fig
    
    def create_region_chart(
        self,
        stats: Dict[str, int],
        chart_type: str = "bar"
    ) -> Figure:
        """Create pie or bar chart showing customer distribution by region."""
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        sorted_stats = dict(
            sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        labels = list(sorted_stats.keys())
        values = list(sorted_stats.values())
        colors = plt.cm.viridis([i / len(values) for i in range(len(values))])
        
        if sum(values) == 0:
            ax.text(
                0.5, 0.5,
                "No region data available",
                ha='center', va='center',
                transform=ax.transAxes,
                fontsize=12
            )
            ax.axis('off')
            return fig
        
        if chart_type.lower() == "pie":
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
            
            ax.set_title("Customer Distribution by Region", fontsize=12, fontweight='bold')
            
        else:
            y_pos = range(len(labels))
            bars = ax.barh(y_pos, values, color=colors)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels)
            ax.invert_yaxis()
            ax.set_xlabel("Number of Customers")
            ax.set_title("Customer Distribution by Region (Top 10)", fontsize=12, fontweight='bold')
            
            for bar, value in zip(bars, values):
                width = bar.get_width()
                ax.annotate(
                    f'{value}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0),
                    textcoords="offset points",
                    ha='left', va='center',
                    fontsize=9
                )
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        fig.tight_layout()
        return fig


if __name__ == "__main__":
    service = ReportService()
    test_stats = {"VIP": 12, "Potential": 18}
    fig = service.create_customer_type_chart(test_stats, "pie")
    fig.savefig("test_chart.png")
    print("Test chart saved to test_chart.png")
