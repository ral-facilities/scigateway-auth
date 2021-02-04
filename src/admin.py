import logging
import json
import jwt

from common.constants import PUBLIC_KEY, BLACKLIST, MAINTENANCE_CONFIG_PATH, \
    SCHEDULED_MAINTENANCE_CONFIG_PATH

log = logging.getLogger()


class MaintenanceMode(object):
    """
    Class that contains functions to get and set the maintenance mode state.
    """

    def get_state(self):
        """
        Reads and returns the maintenance mode state from the maintenance.json file.
        :return: the maintenance mode state in form of a JSON.
        """
        log.info("Attempting to read maintenance mode state")
        with open(MAINTENANCE_CONFIG_PATH, "r") as file:
            return json.load(file)

class ScheduledMaintenanceMode(object):
    """
    Class that contains functions to get and set the scheduled maintenance mode state.
    """

    def get_state(self):
        """
        Reads and returns the scheduled maintenance mode state from the
        scheduled_maintenance.json file.
        :return: The scheduled maintenance mode state in form of a JSON.
        """
        log.info("Attempting to read scheduled maintenance mode state")
        with open(SCHEDULED_MAINTENANCE_CONFIG_PATH, "r") as file:
            return json.load(file)
