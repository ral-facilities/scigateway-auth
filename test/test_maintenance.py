"""
Unit tests for the `MaintenanceBase` class.
"""

import json
from unittest.mock import mock_open, patch

import pytest

from scigateway_auth.common.exceptions import (
    InvalidMaintenanceFileError,
    MaintenanceFileReadError,
    MaintenanceFileWriteError,
)
from scigateway_auth.common.schemas import ScheduledMaintenanceStateSchema
from scigateway_auth.src.maintenance import MaintenanceBase


class TestMaintenanceBase:
    """
    Unit tests for the `MaintenanceBase` class.
    """

    config_path = "path/to/config/test_maintenance.json"
    maintenance_state = ScheduledMaintenanceStateSchema(show=False, message="test-message", severity="test-severity")
    maintenance_base = MaintenanceBase(config_path, ScheduledMaintenanceStateSchema)

    @patch("builtins.open", mock_open(read_data=maintenance_state.model_dump_json()))
    def test_get_maintenance_state(self):
        """
        Test that `get_maintenance_state` successfully reads and returns the maintenance state from the file.
        """
        state = self.maintenance_base.get_maintenance_state()

        assert state == self.maintenance_state

    @patch("builtins.open", side_effect=IOError)
    def test_get_maintenance_state_file_read_error(self, mock_open_file):
        """
        Test that `get_maintenance_state` raises `MaintenanceFileReadError` when an `IOError` occurs while trying to
        read the file.
        """
        with pytest.raises(MaintenanceFileReadError) as exc:
            self.maintenance_base.get_maintenance_state()
        assert str(exc.value) == "An error occurred while trying to find and read the scheduled maintenance file"

    @patch("builtins.open", mock_open(read_data=json.dumps({"show": True})))
    def test_get_maintenance_state_invalid_file(self):
        """
        Test that `get_maintenance_state` raises `InvalidMaintenanceFileError` when the data in the file is invalid and
        cannot be validated.
        """
        with pytest.raises(InvalidMaintenanceFileError) as exc:
            self.maintenance_base.get_maintenance_state()
        assert str(exc.value) == "An error occurred while validating the data in the scheduled maintenance file"

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_update_maintenance_state(self, mock_json_dump, mock_open_file):
        """
        Test that `update_maintenance_state` successfully writes the maintenance state to the file.
        """
        self.maintenance_base.update_maintenance_state(self.maintenance_state)

        mock_open_file.assert_called_once_with(self.config_path, "w")
        mock_json_dump.assert_called_once_with(self.maintenance_state.model_dump(), mock_open_file())

    @patch("builtins.open", side_effect=OSError)
    def test_update_maintenance_state_file_write_error(self, mock_open_file):
        """
        Test that `update_maintenance_state` raises `MaintenanceFileWriteError` when an `OSError` occurs while trying
        to write the maintenance state to the file.
        """
        with pytest.raises(MaintenanceFileWriteError) as exc:
            self.maintenance_base.update_maintenance_state(self.maintenance_state)
        assert str(exc.value) == "An error occurred while trying to find and update the scheduled maintenance file"
        mock_open_file.assert_called_once_with(self.config_path, "w")
