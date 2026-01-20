"""
Unit tests for virtuoso_database module.
Tests for database operation functions.
"""
import pytest
from unittest.mock import Mock, patch, call
import subprocess
from functions.virtuoso_database import (
    load_graphs,
    clear_graphs_only
)


class TestLoadGraphs:
    """Test load_graphs function"""
    
    def test_validates_arguments_are_strings(self):
        """Should raise TypeError if arguments are not strings"""
        with pytest.raises(TypeError):
            load_graphs(directory=123, shapes_file="shapes.ttl", report_file="report.ttl")
        
        with pytest.raises(TypeError):
            load_graphs(directory="/data", shapes_file=None, report_file="report.ttl")
    
    def test_validates_arguments_not_empty(self):
        """Should raise ValueError if arguments are empty"""
        with pytest.raises(ValueError):
            load_graphs(directory="", shapes_file="shapes.ttl", report_file="report.ttl")
        
        with pytest.raises(ValueError):
            load_graphs(directory="/data", shapes_file="  ", report_file="report.ttl")
    
    @patch('functions.virtuoso_database.subprocess.run')
    def test_clears_graphs_before_loading(self, mock_run):
        """Should clear existing graphs before loading new data"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        load_graphs(
            directory="/data",
            shapes_file="shapes.ttl",
            report_file="report.ttl"
        )
        
        # Verify subprocess.run was called (for clearing and loading)
        assert mock_run.called
        assert mock_run.call_count >= 2  # At least 2 clears + load
    
    @patch('functions.virtuoso_database.subprocess.run')
    def test_handles_subprocess_error(self, mock_run):
        """Should handle subprocess errors gracefully"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="Error")
        
        with pytest.raises(RuntimeError):
            load_graphs(
                directory="/data",
                shapes_file="shapes.ttl",
                report_file="report.ttl"
            )


class TestClearGraphsOnly:
    """Test clear_graphs_only function"""
    
    @patch('functions.virtuoso_database.subprocess.run')
    def test_executes_isql_test_command(self, mock_run):
        """Should execute ISQL test command via subprocess"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Test successful",
            stderr=""
        )
        
        clear_graphs_only()
        
        # Verify subprocess.run was called
        assert mock_run.called
        call_args = mock_run.call_args
        assert "docker" in call_args[0][0]
        assert "exec" in call_args[0][0]
    
    @patch('functions.virtuoso_database.subprocess.run')
    def test_handles_isql_failure(self, mock_run):
        """Should handle ISQL command failures gracefully"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="ISQL error"
        )
        
        # Function logs error but doesn't raise
        clear_graphs_only()  # Should not raise exception
