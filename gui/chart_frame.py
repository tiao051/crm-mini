"""Chart frame component for displaying embedded matplotlib charts."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from services.report_service import ReportService


class ChartFrame(ttk.Frame):
    """Tkinter frame with embedded matplotlib charts."""
    
    CHART_COLORS = [
        '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b',
        '#ef4444', '#ec4899', '#6366f1', '#14b8a6',
    ]
    
    def __init__(self, parent: tk.Widget, report_service: ReportService, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.report_service = report_service
        self.chart_type = tk.StringVar(value="pie")
        self.data_type = tk.StringVar(value="customer_type")
        self.type_stats: Dict[str, int] = {}
        self.region_stats: Dict[str, int] = {}
        self.canvas: Optional[FigureCanvasTkAgg] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Chart type selection
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT)
        
        ttk.Label(left_frame, text="Chart:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Radiobutton(left_frame, text="Pie", variable=self.chart_type, value="pie",
                       command=self._refresh_chart).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(left_frame, text="Bar", variable=self.chart_type, value="bar",
                       command=self._refresh_chart).pack(side=tk.LEFT, padx=4)
        
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Data type selection
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.LEFT)
        
        ttk.Label(right_frame, text="Data:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Radiobutton(right_frame, text="Customer Type", variable=self.data_type,
                       value="customer_type", command=self._refresh_chart).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(right_frame, text="Region", variable=self.data_type,
                       value="region", command=self._refresh_chart).pack(side=tk.LEFT, padx=4)
        
        # Chart container
        self.chart_container = ttk.Frame(self)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_empty_chart()
    
    def _create_empty_chart(self) -> None:
        fig = Figure(figsize=(8, 4), dpi=100, facecolor='#f8f9fa')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        ax.text(0.5, 0.5, "Loading chart data...", ha='center', va='center',
               transform=ax.transAxes, fontsize=14, color='#6b7280', fontweight='bold')
        ax.axis('off')
        self._embed_figure(fig)
    
    def _embed_figure(self, figure: Figure) -> None:
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(figure, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_stats(self, type_stats: Dict[str, int], region_stats: Dict[str, int]) -> None:
        self.type_stats = type_stats
        self.region_stats = region_stats
        self._refresh_chart()
    
    def _refresh_chart(self) -> None:
        if self.data_type.get() == "customer_type":
            fig = self._create_type_chart(self.type_stats, self.chart_type.get())
        else:
            fig = self._create_region_chart(self.region_stats, self.chart_type.get())
        self._embed_figure(fig)
    
    def _create_type_chart(self, stats: Dict[str, int], chart_type: str) -> Figure:
        fig = Figure(figsize=(8, 4), dpi=100, facecolor='#f8f9fa')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        
        labels = list(stats.keys())
        values = list(stats.values())
        total = sum(values)
        
        if total == 0:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color='#6b7280')
            ax.axis('off')
            return fig
        
        colors = ['#8b5cf6', '#06b6d4']
        
        if chart_type == "pie":
            wedges, texts, autotexts = ax.pie(
                values, labels=None, autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
                startangle=90, colors=colors[:len(labels)],
                wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2), pctdistance=0.75
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            
            ax.text(0, 0, f'{total}', ha='center', va='center',
                   fontsize=24, fontweight='bold', color='#1f2937')
            ax.text(0, -0.15, 'Total', ha='center', va='center', fontsize=10, color='#6b7280')
            
            legend_labels = [f'{label}: {val}' for label, val in zip(labels, values)]
            ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1.05, 0.5),
                     frameon=False, fontsize=10)
        else:
            x = range(len(labels))
            bars = ax.bar(x, values, color=colors[:len(labels)], edgecolor='white', linewidth=1, width=0.6)
            
            for bar, val in zip(bars, values):
                ax.annotate(f'{val}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                           xytext=(0, 5), textcoords="offset points", ha='center', va='bottom',
                           fontsize=12, fontweight='bold', color='#1f2937')
            
            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=11, fontweight='medium')
            ax.set_ylabel('Number of Customers', fontsize=10, color='#6b7280')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e5e7eb')
            ax.spines['bottom'].set_color('#e5e7eb')
            ax.tick_params(colors='#6b7280')
            ax.set_ylim(0, max(values) * 1.2)
        
        ax.set_title('Customer Type Distribution', fontsize=14, fontweight='bold', color='#1f2937', pad=15)
        fig.tight_layout()
        return fig
    
    def _create_region_chart(self, stats: Dict[str, int], chart_type: str) -> Figure:
        fig = Figure(figsize=(8, 4), dpi=100, facecolor='#f8f9fa')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        
        # Limit to top 8 regions
        sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True)[:8])
        labels = list(sorted_stats.keys())
        values = list(sorted_stats.values())
        total = sum(values)
        
        if total == 0:
            ax.text(0.5, 0.5, "No region data available", ha='center', va='center',
                   transform=ax.transAxes, fontsize=14, color='#6b7280')
            ax.axis('off')
            return fig
        
        short_labels = [l[:12] + '...' if len(l) > 15 else l for l in labels]
        
        if chart_type == "pie":
            wedges, texts, autotexts = ax.pie(
                values, labels=None, autopct=lambda pct: f'{pct:.0f}%' if pct > 8 else '',
                startangle=90, colors=self.CHART_COLORS[:len(labels)],
                wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2), pctdistance=0.78
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            ax.text(0, 0, f'{total}', ha='center', va='center',
                   fontsize=22, fontweight='bold', color='#1f2937')
            ax.text(0, -0.12, 'Regions', ha='center', va='center', fontsize=9, color='#6b7280')
            
            legend_labels = [f'{l}: {v}' for l, v in zip(short_labels, values)]
            ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1.02, 0.5),
                     frameon=False, fontsize=9)
        else:
            # Horizontal bar chart for regions
            y = range(len(labels))
            bars = ax.barh(y, values, color=self.CHART_COLORS[:len(labels)],
                          edgecolor='white', linewidth=1, height=0.7)
            
            for bar, val in zip(bars, values):
                ax.annotate(f'{val}', xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                           xytext=(5, 0), textcoords="offset points", ha='left', va='center',
                           fontsize=10, fontweight='bold', color='#1f2937')
            
            ax.set_yticks(y)
            ax.set_yticklabels(short_labels, fontsize=10)
            ax.invert_yaxis()
            ax.set_xlabel('Number of Customers', fontsize=10, color='#6b7280')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e5e7eb')
            ax.spines['bottom'].set_color('#e5e7eb')
            ax.tick_params(colors='#6b7280')
            ax.set_xlim(0, max(values) * 1.25)
        
        ax.set_title('Top Regions by Customers', fontsize=14, fontweight='bold', color='#1f2937', pad=15)
        fig.tight_layout()
        return fig
    
    def refresh(self) -> None:
        self._refresh_chart()
