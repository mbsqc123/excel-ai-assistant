"""
Visualization Dialog for Excel AI Assistant
Provides UI for creating and customizing data visualizations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from app.services.visualization_manager import VisualizationManager

logger = logging.getLogger(__name__)


class VisualizationDialog:
    """Dialog for creating and customizing data visualizations"""

    def __init__(self, parent, data: pd.DataFrame, theme_manager=None):
        """
        Initialize the visualization dialog

        Args:
            parent: Parent window
            data: DataFrame containing the data to visualize
            theme_manager: ThemeManager instance for styling
        """
        self.parent = parent
        self.data = data
        self.theme_manager = theme_manager
        self.viz_manager = VisualizationManager()
        self.current_figure = None
        self.canvas = None
        self.toolbar = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Data Visualization Tool")
        self.dialog.geometry("1200x800")
        self.dialog.minsize(1000, 700)

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Apply theme if available
        if self.theme_manager:
            self._apply_theme()

        # Create UI
        self._create_ui()

        # Center dialog on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        logger.info("Visualization dialog opened")

    def _apply_theme(self):
        """Apply theme colors to dialog"""
        colors = self.theme_manager.get_colors()
        self.dialog.configure(bg=colors['bg'])

    def _create_ui(self):
        """Create the user interface"""
        # Create main container with paned window
        paned = ttk.PanedWindow(self.dialog, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Controls
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Right panel - Chart display
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        # Create control panels
        self._create_controls(left_frame)

        # Create chart display area
        self._create_chart_display(right_frame)

    def _create_controls(self, parent):
        """Create control panel with chart options"""
        # Create scrollable frame for controls
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Chart Type Selection
        type_frame = ttk.LabelFrame(scrollable_frame, text="Chart Type", padding=10)
        type_frame.pack(fill=tk.X, padx=5, pady=5)

        self.chart_type_var = tk.StringVar(value='line')
        row = 0
        for chart_key, chart_label in self.viz_manager.CHART_TYPES.items():
            ttk.Radiobutton(
                type_frame,
                text=chart_label,
                variable=self.chart_type_var,
                value=chart_key,
                command=self._on_chart_type_changed
            ).grid(row=row, column=0, sticky=tk.W, pady=2)
            row += 1

        # Data Selection
        data_frame = ttk.LabelFrame(scrollable_frame, text="Data Selection", padding=10)
        data_frame.pack(fill=tk.X, padx=5, pady=5)

        # X-axis column
        ttk.Label(data_frame, text="X-Axis Column:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.x_column_var = tk.StringVar()
        self.x_column_combo = ttk.Combobox(
            data_frame,
            textvariable=self.x_column_var,
            values=self.viz_manager.get_all_columns(self.data),
            state='readonly',
            width=25
        )
        self.x_column_combo.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        if len(self.data.columns) > 0:
            self.x_column_combo.current(0)

        # Y-axis column
        ttk.Label(data_frame, text="Y-Axis Column:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.y_column_var = tk.StringVar()
        self.y_column_combo = ttk.Combobox(
            data_frame,
            textvariable=self.y_column_var,
            values=self.viz_manager.get_all_columns(self.data),
            state='readonly',
            width=25
        )
        self.y_column_combo.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        if len(self.data.columns) > 1:
            self.y_column_combo.current(1)

        # Hue/Group column (optional)
        ttk.Label(data_frame, text="Group By (Optional):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.hue_column_var = tk.StringVar()
        self.hue_column_combo = ttk.Combobox(
            data_frame,
            textvariable=self.hue_column_var,
            values=['None'] + self.viz_manager.get_all_columns(self.data),
            state='readonly',
            width=25
        )
        self.hue_column_combo.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        self.hue_column_combo.current(0)

        data_frame.columnconfigure(1, weight=1)

        # Appearance Settings
        appearance_frame = ttk.LabelFrame(scrollable_frame, text="Appearance", padding=10)
        appearance_frame.pack(fill=tk.X, padx=5, pady=5)

        # Title
        ttk.Label(appearance_frame, text="Chart Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value="Data Visualization")
        ttk.Entry(appearance_frame, textvariable=self.title_var, width=25).grid(
            row=0, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # X-axis label
        ttk.Label(appearance_frame, text="X-Axis Label:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.xlabel_var = tk.StringVar()
        ttk.Entry(appearance_frame, textvariable=self.xlabel_var, width=25).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Y-axis label
        ttk.Label(appearance_frame, text="Y-Axis Label:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ylabel_var = tk.StringVar()
        ttk.Entry(appearance_frame, textvariable=self.ylabel_var, width=25).grid(
            row=2, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Color palette
        ttk.Label(appearance_frame, text="Color Palette:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.palette_var = tk.StringVar(value='default')
        palette_combo = ttk.Combobox(
            appearance_frame,
            textvariable=self.palette_var,
            values=list(self.viz_manager.COLOR_PALETTES.values()),
            state='readonly',
            width=25
        )
        palette_combo.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        palette_combo.current(0)

        # Figure size
        ttk.Label(appearance_frame, text="Figure Size:").grid(row=4, column=0, sticky=tk.W, pady=5)
        size_frame = ttk.Frame(appearance_frame)
        size_frame.grid(row=4, column=1, sticky=tk.EW, pady=5, padx=5)

        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT)
        self.fig_width_var = tk.IntVar(value=10)
        ttk.Spinbox(size_frame, from_=5, to=20, textvariable=self.fig_width_var, width=5).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        self.fig_height_var = tk.IntVar(value=6)
        ttk.Spinbox(size_frame, from_=3, to=15, textvariable=self.fig_height_var, width=5).pack(
            side=tk.LEFT, padx=5
        )

        # Show grid
        self.show_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            appearance_frame,
            text="Show Grid",
            variable=self.show_grid_var
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Show legend
        self.show_legend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            appearance_frame,
            text="Show Legend",
            variable=self.show_legend_var
        ).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        appearance_frame.columnconfigure(1, weight=1)

        # Advanced Options (for specific chart types)
        advanced_frame = ttk.LabelFrame(scrollable_frame, text="Advanced Options", padding=10)
        advanced_frame.pack(fill=tk.X, padx=5, pady=5)

        # Bins (for histogram)
        ttk.Label(advanced_frame, text="Histogram Bins:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bins_var = tk.IntVar(value=30)
        ttk.Spinbox(advanced_frame, from_=5, to=100, textvariable=self.bins_var, width=10).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=5
        )

        advanced_frame.columnconfigure(1, weight=1)

        # Action Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Button(
            button_frame,
            text="Generate Chart",
            command=self._generate_chart,
            style='Accent.TButton'
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            button_frame,
            text="Export Chart...",
            command=self._export_chart
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(fill=tk.X, pady=2)

    def _create_chart_display(self, parent):
        """Create chart display area"""
        # Title
        title_label = ttk.Label(
            parent,
            text="Chart Preview",
            font=('TkDefaultFont', 12, 'bold')
        )
        title_label.pack(pady=10)

        # Chart frame
        self.chart_frame = ttk.Frame(parent)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Info label for when no chart is displayed
        self.info_label = ttk.Label(
            self.chart_frame,
            text="Click 'Generate Chart' to create a visualization",
            font=('TkDefaultFont', 11)
        )
        self.info_label.pack(expand=True)

    def _on_chart_type_changed(self):
        """Handle chart type selection change"""
        chart_type = self.chart_type_var.get()

        # Update column selection based on chart type
        if chart_type in ['pie', 'histogram', 'kde', 'count']:
            # These charts typically use only one data column
            self.y_column_combo.configure(state='disabled')
        else:
            self.y_column_combo.configure(state='readonly')

        # Update available columns based on chart requirements
        if chart_type == 'heatmap':
            # Heatmap uses all numeric columns
            self.x_column_combo.configure(state='disabled')
            self.y_column_combo.configure(state='disabled')
        else:
            self.x_column_combo.configure(state='readonly')

    def _generate_chart(self):
        """Generate and display the chart"""
        try:
            # Get parameters
            chart_type = self.chart_type_var.get()
            x_column = self.x_column_var.get() if self.x_column_var.get() else None
            y_column = self.y_column_var.get() if self.y_column_var.get() else None
            hue_column = self.hue_column_var.get() if self.hue_column_var.get() != 'None' else None
            title = self.title_var.get()
            xlabel = self.xlabel_var.get()
            ylabel = self.ylabel_var.get()

            # Get color palette key from display value
            palette_display = self.palette_var.get()
            palette_key = [k for k, v in self.viz_manager.COLOR_PALETTES.items() if v == palette_display][0]

            figsize = (self.fig_width_var.get(), self.fig_height_var.get())
            show_grid = self.show_grid_var.get()
            show_legend = self.show_legend_var.get()

            # Advanced options
            bins = self.bins_var.get()

            # Validate inputs
            if chart_type != 'heatmap' and not x_column:
                messagebox.showerror("Error", "Please select an X-axis column")
                return

            if chart_type not in ['pie', 'histogram', 'kde', 'count', 'heatmap'] and not y_column:
                messagebox.showerror("Error", "Please select a Y-axis column")
                return

            # Create the chart
            self.current_figure = self.viz_manager.create_chart(
                data=self.data,
                chart_type=chart_type,
                x_column=x_column,
                y_column=y_column,
                hue_column=hue_column,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                color_palette=palette_key,
                figsize=figsize,
                show_grid=show_grid,
                show_legend=show_legend,
                bins=bins
            )

            # Display the chart
            self._display_chart(self.current_figure)

            logger.info(f"Generated {chart_type} chart successfully")

        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate chart:\n{str(e)}")

    def _display_chart(self, figure: Figure):
        """Display a matplotlib figure in the chart frame"""
        # Clear previous chart
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()
        if self.info_label:
            self.info_label.destroy()
            self.info_label = None

        # Create new canvas
        self.canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        toolbar_frame = ttk.Frame(self.chart_frame)
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def _export_chart(self):
        """Export the current chart to a file"""
        if not self.current_figure:
            messagebox.showwarning("Warning", "Please generate a chart first")
            return

        # Ask user for file path
        filetypes = [
            ("PNG Image", "*.png"),
            ("PDF Document", "*.pdf"),
            ("SVG Vector", "*.svg"),
            ("JPEG Image", "*.jpg"),
            ("All Files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            parent=self.dialog,
            title="Export Chart",
            defaultextension=".png",
            filetypes=filetypes
        )

        if filepath:
            try:
                self.viz_manager.save_chart(self.current_figure, filepath)
                messagebox.showinfo("Success", f"Chart exported successfully to:\n{filepath}")
                logger.info(f"Chart exported to {filepath}")
            except Exception as e:
                logger.error(f"Error exporting chart: {str(e)}")
                messagebox.showerror("Error", f"Failed to export chart:\n{str(e)}")
