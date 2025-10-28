"""
Unit tests for DataManager class.
Tests data loading, saving, and manipulation operations.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from app.services.data_manager import DataManager


class TestDataManagerInit:
    """Test DataManager initialization."""

    def test_init(self):
        """Test DataManager initialization with default values."""
        dm = DataManager()
        assert dm.df is None
        assert dm.file_path is None
        assert dm.file_type is None
        assert dm.modified is False


class TestDataManagerLoadFile:
    """Test file loading functionality."""

    @pytest.mark.unit
    def test_load_csv_file(self, sample_csv_file):
        """Test loading a CSV file."""
        dm = DataManager()
        success, error = dm.load_file(str(sample_csv_file))

        assert success is True
        assert error == ""
        assert dm.df is not None
        assert len(dm.df) == 4
        assert 'Name' in dm.df.columns
        assert dm.file_type == 'csv'
        assert dm.modified is False

    @pytest.mark.unit
    def test_load_excel_file(self, sample_excel_file):
        """Test loading an Excel file."""
        dm = DataManager()
        success, error = dm.load_file(str(sample_excel_file))

        assert success is True
        assert error == ""
        assert dm.df is not None
        assert len(dm.df) == 4
        assert 'Product' in dm.df.columns
        assert dm.file_type == 'excel'

    @pytest.mark.unit
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        dm = DataManager()
        success, error = dm.load_file("/nonexistent/path/file.csv")

        assert success is False
        assert "not found" in error.lower()
        assert dm.df is None

    @pytest.mark.unit
    def test_load_unsupported_format(self, temp_dir):
        """Test loading an unsupported file format."""
        # Create a text file
        text_file = temp_dir / "test.txt"
        text_file.write_text("This is not a spreadsheet")

        dm = DataManager()
        success, error = dm.load_file(str(text_file))

        assert success is False
        assert "unsupported" in error.lower()

    @pytest.mark.unit
    def test_load_empty_file(self, temp_dir):
        """Test loading an empty CSV file."""
        empty_file = temp_dir / "empty.csv"
        empty_file.write_text("")

        dm = DataManager()
        success, error = dm.load_file(str(empty_file))

        assert success is False
        assert dm.df is None

    @pytest.mark.unit
    def test_column_name_cleanup(self, temp_dir):
        """Test that column names are properly cleaned up."""
        # Create CSV with spaces in column names
        csv_file = temp_dir / "spaces.csv"
        csv_file.write_text(" Name , Age , City \nJohn,30,NYC")

        dm = DataManager()
        success, error = dm.load_file(str(csv_file))

        assert success is True
        # Check that spaces are stripped
        assert 'Name' in dm.df.columns
        assert 'Age' in dm.df.columns
        assert 'City' in dm.df.columns


class TestDataManagerSaveFile:
    """Test file saving functionality."""

    @pytest.mark.unit
    def test_save_csv(self, sample_csv_file, temp_dir):
        """Test saving data to CSV."""
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        output_file = temp_dir / "output.csv"
        success, error = dm.save_file(str(output_file))

        assert success is True
        assert error == ""
        assert output_file.exists()
        assert dm.modified is False

    @pytest.mark.unit
    def test_save_excel(self, sample_excel_file, temp_dir):
        """Test saving data to Excel."""
        dm = DataManager()
        dm.load_file(str(sample_excel_file))

        output_file = temp_dir / "output.xlsx"
        success, error = dm.save_file(str(output_file))

        assert success is True
        assert output_file.exists()

    @pytest.mark.unit
    def test_save_without_data(self):
        """Test saving when no data is loaded."""
        dm = DataManager()
        success, error = dm.save_file("/tmp/test.csv")

        assert success is False
        assert "no data" in error.lower()

    @pytest.mark.unit
    def test_save_to_current_path(self, sample_csv_file, temp_dir):
        """Test saving to the current file path."""
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        # Modify data
        dm.df.loc[0, 'Name'] = 'Modified Name'
        dm.modified = True

        success, error = dm.save_file()
        assert success is True
        assert dm.modified is False

    @pytest.mark.unit
    def test_save_adds_extension(self, sample_csv_file, temp_dir):
        """Test that save adds default extension if missing."""
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        output_file = temp_dir / "output_no_ext"
        success, error = dm.save_file(str(output_file))

        assert success is True
        # Should add .xlsx extension
        assert (temp_dir / "output_no_ext.xlsx").exists()


class TestDataManagerGetData:
    """Test data retrieval methods."""

    @pytest.mark.unit
    def test_get_data(self, sample_dataframe):
        """Test getting the DataFrame."""
        dm = DataManager()
        dm.df = sample_dataframe

        result = dm.get_data()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_dataframe)

    @pytest.mark.unit
    def test_get_meta_info_no_data(self):
        """Test getting metadata when no data is loaded."""
        dm = DataManager()
        meta = dm.get_meta_info()

        assert meta['loaded'] is False

    @pytest.mark.unit
    def test_get_meta_info_with_data(self, sample_csv_file):
        """Test getting metadata with loaded data."""
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        meta = dm.get_meta_info()

        assert meta['loaded'] is True
        assert meta['rows'] == 4
        assert meta['columns'] == 5
        assert 'Name' in meta['column_names']
        assert meta['file_type'] == 'csv'
        assert meta['modified'] is False

    @pytest.mark.unit
    def test_get_column_data_types(self, sample_dataframe):
        """Test getting column data types."""
        dm = DataManager()
        dm.df = sample_dataframe

        types = dm.get_column_data_types()

        assert types['Text'] == 'text'
        assert types['Numbers'] == 'integer'
        assert types['Floats'] == 'float'
        assert types['Dates'] == 'datetime'


class TestDataManagerCellOperations:
    """Test cell-level operations."""

    @pytest.mark.unit
    def test_get_cell_value(self, sample_dataframe):
        """Test getting a cell value."""
        dm = DataManager()
        dm.df = sample_dataframe

        value = dm.get_cell_value(0, 'Text')
        assert value == 'hello world'

    @pytest.mark.unit
    def test_get_cell_value_invalid_row(self, sample_dataframe):
        """Test getting cell value with invalid row."""
        dm = DataManager()
        dm.df = sample_dataframe

        value = dm.get_cell_value(999, 'Text')
        assert value is None

    @pytest.mark.unit
    def test_get_cell_value_invalid_column(self, sample_dataframe):
        """Test getting cell value with invalid column."""
        dm = DataManager()
        dm.df = sample_dataframe

        value = dm.get_cell_value(0, 'NonExistent')
        assert value is None

    @pytest.mark.unit
    def test_update_cell(self, sample_dataframe):
        """Test updating a cell value."""
        dm = DataManager()
        dm.df = sample_dataframe

        success = dm.update_cell(0, 'Text', 'updated value')

        assert success is True
        assert dm.df.loc[0, 'Text'] == 'updated value'
        assert dm.modified is True

    @pytest.mark.unit
    def test_update_cell_invalid(self, sample_dataframe):
        """Test updating an invalid cell."""
        dm = DataManager()
        dm.df = sample_dataframe

        success = dm.update_cell(999, 'Text', 'value')
        assert success is False


class TestDataManagerRangeOperations:
    """Test range operations."""

    @pytest.mark.unit
    def test_update_range(self, sample_dataframe):
        """Test updating multiple cells."""
        dm = DataManager()
        dm.df = sample_dataframe

        updates = [
            {'row': 0, 'col': 'Text', 'result': 'updated 1'},
            {'row': 1, 'col': 'Text', 'result': 'updated 2'},
            {'row': 2, 'col': 'Text', 'result': 'updated 3'}
        ]

        success_count, error_count = dm.update_range(updates)

        assert success_count == 3
        assert error_count == 0
        assert dm.modified is True
        assert dm.df.loc[0, 'Text'] == 'updated 1'

    @pytest.mark.unit
    def test_update_range_with_errors(self, sample_dataframe):
        """Test updating range with some invalid updates."""
        dm = DataManager()
        dm.df = sample_dataframe

        updates = [
            {'row': 0, 'col': 'Text', 'result': 'valid'},
            {'row': 999, 'col': 'Text', 'result': 'invalid row'},
            {'row': 0, 'col': 'Invalid', 'result': 'invalid col'}
        ]

        success_count, error_count = dm.update_range(updates)

        assert success_count == 1
        assert error_count == 2

    @pytest.mark.unit
    def test_get_range(self, sample_dataframe):
        """Test getting a range of cells."""
        dm = DataManager()
        dm.df = sample_dataframe

        cells = dm.get_range(0, 2, ['Text', 'Numbers'])

        assert len(cells) == 4  # 2 rows * 2 columns
        assert cells[0]['row'] == 0
        assert cells[0]['col'] == 'Text'
        assert cells[0]['content'] == 'hello world'

    @pytest.mark.unit
    def test_get_range_with_context(self, sample_dataframe):
        """Test getting range with context columns."""
        dm = DataManager()
        dm.df = sample_dataframe

        cells = dm.get_range(0, 2, ['Text'], context_columns=['Numbers', 'Floats'])

        assert len(cells) == 2
        assert 'context_data' in cells[0]
        assert 'Numbers' in cells[0]['context_data']
        assert 'Floats' in cells[0]['context_data']

    @pytest.mark.unit
    def test_get_range_validates_bounds(self, sample_dataframe):
        """Test that get_range validates row bounds."""
        dm = DataManager()
        dm.df = sample_dataframe

        # Request range beyond data
        cells = dm.get_range(0, 1000, ['Text'])

        # Should only return available rows
        assert len(cells) == 4  # Only 4 rows in sample data


class TestDataManagerAnalysis:
    """Test data analysis methods."""

    @pytest.mark.unit
    def test_get_data_summary(self, sample_dataframe):
        """Test getting data summary."""
        dm = DataManager()
        dm.df = sample_dataframe

        summary = dm.get_data_summary()

        assert summary['rows'] == 4
        assert summary['columns'] == 4
        assert 'column_types' in summary
        assert 'column_stats' in summary

    @pytest.mark.unit
    def test_analyze_numeric_column(self, sample_dataframe):
        """Test analyzing a numeric column."""
        dm = DataManager()
        dm.df = sample_dataframe

        analysis = dm.analyze_column('Numbers')

        assert analysis['type'] == 'integer'
        assert analysis['count'] == 4
        assert analysis['min'] == 10
        assert analysis['max'] == 40
        assert 'mean' in analysis
        assert 'histogram' in analysis

    @pytest.mark.unit
    def test_analyze_text_column(self, sample_dataframe):
        """Test analyzing a text column."""
        dm = DataManager()
        dm.df = sample_dataframe

        analysis = dm.analyze_column('Text')

        assert analysis['type'] == 'text'
        assert analysis['unique'] == 4
        assert 'most_common' in analysis

    @pytest.mark.unit
    def test_analyze_nonexistent_column(self):
        """Test analyzing a column that doesn't exist."""
        dm = DataManager()
        dm.df = pd.DataFrame({'A': [1, 2, 3]})

        analysis = dm.analyze_column('NonExistent')

        assert 'error' in analysis


class TestDataManagerEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.unit
    def test_operations_on_empty_manager(self):
        """Test operations when no data is loaded."""
        dm = DataManager()

        assert dm.get_data() is None
        assert dm.get_column_data_types() == {}
        assert dm.get_range(0, 10, ['A']) == []

    @pytest.mark.unit
    def test_handle_nan_values(self, temp_dir):
        """Test handling of NaN values."""
        # Create CSV with missing values
        csv_file = temp_dir / "missing.csv"
        csv_file.write_text("A,B,C\n1,2,3\n4,,6\n,,9")

        dm = DataManager()
        success, _ = dm.load_file(str(csv_file))

        assert success is True
        # NaN should be replaced with None
        assert dm.df.loc[1, 'B'] is None or pd.isna(dm.df.loc[1, 'B'])

    @pytest.mark.unit
    def test_modified_flag_updates(self, sample_dataframe):
        """Test that modified flag is properly updated."""
        dm = DataManager()
        dm.df = sample_dataframe
        dm.modified = False

        # Update cell should set modified
        dm.update_cell(0, 'Text', 'new value')
        assert dm.modified is True

        # Save should reset modified
        dm.modified = False
        assert dm.modified is False
