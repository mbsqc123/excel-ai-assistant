"""
Data Visualization Manager for Excel AI Assistant
Handles creation of various chart types using matplotlib and seaborn
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
import logging
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class VisualizationManager:
    """Manages data visualization operations"""

    # Chart types supported
    CHART_TYPES = {
        'line': 'Line Chart',
        'bar': 'Bar Chart',
        'horizontal_bar': 'Horizontal Bar Chart',
        'scatter': 'Scatter Plot',
        'pie': 'Pie Chart',
        'histogram': 'Histogram',
        'box': 'Box Plot',
        'violin': 'Violin Plot',
        'heatmap': 'Heatmap',
        'area': 'Area Chart',
        'kde': 'KDE Plot (Density)',
        'count': 'Count Plot'
    }

    # Color palettes available
    COLOR_PALETTES = {
        'default': 'Default',
        'deep': 'Deep',
        'muted': 'Muted',
        'pastel': 'Pastel',
        'bright': 'Bright',
        'dark': 'Dark',
        'colorblind': 'Colorblind-friendly',
        'viridis': 'Viridis',
        'plasma': 'Plasma',
        'inferno': 'Inferno',
        'magma': 'Magma',
        'cividis': 'Cividis'
    }

    def __init__(self):
        """Initialize the visualization manager"""
        self.style = 'default'
        self.dpi = 100
        sns.set_theme()

    def set_style(self, style: str = 'default'):
        """
        Set the matplotlib/seaborn style

        Args:
            style: Style name (e.g., 'default', 'darkgrid', 'whitegrid', 'dark', 'white', 'ticks')
        """
        self.style = style
        if style == 'default':
            sns.set_theme()
        else:
            sns.set_style(style)

    def create_chart(
        self,
        data: pd.DataFrame,
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        hue_column: Optional[str] = None,
        title: str = '',
        xlabel: str = '',
        ylabel: str = '',
        color_palette: str = 'default',
        figsize: tuple = (10, 6),
        show_grid: bool = True,
        show_legend: bool = True,
        **kwargs
    ) -> Figure:
        """
        Create a chart based on the specified type and parameters

        Args:
            data: DataFrame containing the data to visualize
            chart_type: Type of chart to create
            x_column: Column name for x-axis
            y_column: Column name for y-axis
            hue_column: Column name for color grouping
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            color_palette: Color palette to use
            figsize: Figure size (width, height)
            show_grid: Whether to show grid
            show_legend: Whether to show legend
            **kwargs: Additional chart-specific parameters

        Returns:
            matplotlib Figure object
        """
        try:
            # Create figure
            fig = Figure(figsize=figsize, dpi=self.dpi)
            ax = fig.add_subplot(111)

            # Set color palette
            if color_palette != 'default':
                sns.set_palette(color_palette)

            # Create the appropriate chart type
            if chart_type == 'line':
                self._create_line_chart(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'bar':
                self._create_bar_chart(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'horizontal_bar':
                self._create_horizontal_bar_chart(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'scatter':
                self._create_scatter_plot(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'pie':
                self._create_pie_chart(ax, data, x_column, y_column, **kwargs)

            elif chart_type == 'histogram':
                self._create_histogram(ax, data, x_column, **kwargs)

            elif chart_type == 'box':
                self._create_box_plot(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'violin':
                self._create_violin_plot(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'heatmap':
                self._create_heatmap(ax, data, **kwargs)

            elif chart_type == 'area':
                self._create_area_chart(ax, data, x_column, y_column, hue_column, **kwargs)

            elif chart_type == 'kde':
                self._create_kde_plot(ax, data, x_column, **kwargs)

            elif chart_type == 'count':
                self._create_count_plot(ax, data, x_column, hue_column, **kwargs)

            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            # Set labels and title
            if title:
                ax.set_title(title, fontsize=14, fontweight='bold')
            if xlabel:
                ax.set_xlabel(xlabel, fontsize=11)
            if ylabel:
                ax.set_ylabel(ylabel, fontsize=11)

            # Configure grid
            ax.grid(show_grid, alpha=0.3)

            # Configure legend
            if show_legend and hue_column and chart_type != 'pie':
                ax.legend(title=hue_column)

            # Adjust layout to prevent label cutoff
            fig.tight_layout()

            logger.info(f"Created {chart_type} chart successfully")
            return fig

        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {str(e)}")
            raise

    def _create_line_chart(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create a line chart"""
        if hue_column:
            for label in data[hue_column].unique():
                subset = data[data[hue_column] == label]
                ax.plot(subset[x_column], subset[y_column], label=label, marker='o', **kwargs)
        else:
            ax.plot(data[x_column], data[y_column], marker='o', **kwargs)

    def _create_bar_chart(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create a bar chart"""
        if hue_column:
            sns.barplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=ax, **kwargs)
        else:
            sns.barplot(data=data, x=x_column, y=y_column, ax=ax, **kwargs)

    def _create_horizontal_bar_chart(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create a horizontal bar chart"""
        if hue_column:
            sns.barplot(data=data, x=y_column, y=x_column, hue=hue_column, ax=ax, orient='h', **kwargs)
        else:
            sns.barplot(data=data, x=y_column, y=x_column, ax=ax, orient='h', **kwargs)

    def _create_scatter_plot(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create a scatter plot"""
        if hue_column:
            sns.scatterplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=ax, **kwargs)
        else:
            sns.scatterplot(data=data, x=x_column, y=y_column, ax=ax, **kwargs)

    def _create_pie_chart(self, ax, data, x_column, y_column, **kwargs):
        """Create a pie chart"""
        if y_column:
            sizes = data.groupby(x_column)[y_column].sum()
        else:
            sizes = data[x_column].value_counts()

        ax.pie(sizes, labels=sizes.index, autopct='%1.1f%%', startangle=90, **kwargs)
        ax.axis('equal')

    def _create_histogram(self, ax, data, x_column, **kwargs):
        """Create a histogram"""
        bins = kwargs.pop('bins', 30)
        sns.histplot(data=data, x=x_column, bins=bins, kde=True, ax=ax, **kwargs)

    def _create_box_plot(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create a box plot"""
        if y_column:
            sns.boxplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=ax, **kwargs)
        else:
            sns.boxplot(data=data, y=x_column, ax=ax, **kwargs)

    def _create_violin_plot(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create a violin plot"""
        if y_column:
            sns.violinplot(data=data, x=x_column, y=y_column, hue=hue_column, ax=ax, **kwargs)
        else:
            sns.violinplot(data=data, y=x_column, ax=ax, **kwargs)

    def _create_heatmap(self, ax, data, **kwargs):
        """Create a heatmap of correlation matrix"""
        # Select only numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        if numeric_data.empty:
            raise ValueError("No numeric columns found for heatmap")

        corr_matrix = numeric_data.corr()
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=ax, **kwargs)

    def _create_area_chart(self, ax, data, x_column, y_column, hue_column, **kwargs):
        """Create an area chart"""
        if hue_column:
            for label in data[hue_column].unique():
                subset = data[data[hue_column] == label]
                ax.fill_between(subset[x_column], subset[y_column], alpha=0.5, label=label, **kwargs)
        else:
            ax.fill_between(data[x_column], data[y_column], alpha=0.5, **kwargs)

    def _create_kde_plot(self, ax, data, x_column, **kwargs):
        """Create a KDE (kernel density estimation) plot"""
        sns.kdeplot(data=data, x=x_column, ax=ax, fill=True, **kwargs)

    def _create_count_plot(self, ax, data, x_column, hue_column, **kwargs):
        """Create a count plot"""
        if hue_column:
            sns.countplot(data=data, x=x_column, hue=hue_column, ax=ax, **kwargs)
        else:
            sns.countplot(data=data, x=x_column, ax=ax, **kwargs)

    def get_numeric_columns(self, data: pd.DataFrame) -> List[str]:
        """
        Get list of numeric columns from DataFrame

        Args:
            data: DataFrame to analyze

        Returns:
            List of numeric column names
        """
        return data.select_dtypes(include=[np.number]).columns.tolist()

    def get_categorical_columns(self, data: pd.DataFrame) -> List[str]:
        """
        Get list of categorical columns from DataFrame

        Args:
            data: DataFrame to analyze

        Returns:
            List of categorical column names
        """
        return data.select_dtypes(include=['object', 'category']).columns.tolist()

    def get_all_columns(self, data: pd.DataFrame) -> List[str]:
        """
        Get list of all columns from DataFrame

        Args:
            data: DataFrame to analyze

        Returns:
            List of all column names
        """
        return data.columns.tolist()

    def save_chart(self, fig: Figure, filepath: str, dpi: int = 300):
        """
        Save chart to file

        Args:
            fig: matplotlib Figure object
            filepath: Path where to save the file
            dpi: Resolution (dots per inch)
        """
        try:
            fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
            logger.info(f"Chart saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving chart: {str(e)}")
            raise
