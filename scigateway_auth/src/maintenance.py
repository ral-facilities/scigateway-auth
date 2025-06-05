"""
Module for providing classes for handling maintenance modes.
"""

import json
import logging
from typing import Type, Union

from pydantic import ValidationError

from scigateway_auth.common.config import config
from scigateway_auth.common.exceptions import (
    InvalidMaintenanceFileError,
    MaintenanceFileReadError,
    MaintenanceFileWriteError,
)
from scigateway_auth.common.schemas import MaintenanceStateSchema, ScheduledMaintenanceStateSchema

logger = logging.getLogger()


class MaintenanceBase:
    """
    Base class for managing maintenance states.
    """

    def __init__(
        self,
        config_path: str,
        state_schema_class: Union[Type[MaintenanceStateSchema], Type[ScheduledMaintenanceStateSchema]],
    ) -> None:
        """
        Initialise the base maintenance class.

        :param config_path: The path to the file where the maintenance state is stored.
        :param state_schema_class: The state schema class to use to validate the content of the file.
        """
        self._config_path = config_path
        self._state_schema_class = state_schema_class
        self._state_description = self._get_state_description()

    def _get_state_description(self):
        """
        Return the state description to be used in logging based on the type of the state schema class.

        :return: The state description to be used in logging.
        """
        if self._state_schema_class is MaintenanceStateSchema:
            return "maintenance"

        if self._state_schema_class is ScheduledMaintenanceStateSchema:
            return "scheduled maintenance"

    def get_maintenance_state(self) -> Union[MaintenanceStateSchema, ScheduledMaintenanceStateSchema]:
        """
        Read and return the maintenance state from the file.

        :raises InvalidMaintenanceFileError: If the maintenance file is incorrectly formatted.
        :raises MaintenanceFileReadError: If the maintenance file cannot be found or read.
        :return: The maintenance state.
        """
        logger.info("Attempting to get %s state", self._state_description)
        try:
            with open(self._config_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return self._state_schema_class(**data)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            message = f"An error occurred while trying to find and read the {self._state_description} file"
            logger.exception(message)
            raise MaintenanceFileReadError(message) from exc
        except ValidationError as exc:
            message = f"An error occurred while validating the data in the {self._state_description} file"
            logger.exception(message)
            raise InvalidMaintenanceFileError(message) from exc

    def update_maintenance_state(
        self,
        maintenance_state: Union[MaintenanceStateSchema, ScheduledMaintenanceStateSchema],
    ) -> None:
        """
        Update the maintenance state in the file.

        :param maintenance_state: The state the JSON file to be updated with.
        :raises MaintenanceFileWriteError: If the maintenance file cannot be found or updated.
        """
        logger.info("Attempting to update %s state", self._state_description)
        try:
            with open(self._config_path, "w") as file:
                json.dump(maintenance_state.model_dump(), file)
            logger.info("The %s file was successfully updated", self._state_description)
        except (OSError, OverflowError, TypeError, ValueError) as exc:
            message = f"An error occurred while trying to find and update the {self._state_description} file"
            logger.exception(message)
            raise MaintenanceFileWriteError(message) from exc


class MaintenanceMode(MaintenanceBase):
    """
    Class inheriting from `MaintenanceBase` for managing the maintenance mode using `MaintenanceStateSchema`.
    """

    def __init__(self) -> None:
        """
        Initialise the base maintenance class.
        """
        super().__init__(config.maintenance.maintenance_path, MaintenanceStateSchema)


class ScheduledMaintenanceMode(MaintenanceBase):
    """
    Class inheriting from `MaintenanceBase` for managing the scheduled maintenance mode using
    `ScheduledMaintenanceStateSchema`.
    """

    def __init__(self) -> None:
        """
        Initialise the base maintenance class.
        """
        super().__init__(config.maintenance.scheduled_maintenance_path, ScheduledMaintenanceStateSchema)
