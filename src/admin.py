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

    def set_state(self, access_token, state):
        """
        Updates the maintenance mode state in the maintenance.json file.
        :param access_token: the access token to be verified
        :param state: the state the JSON file to be updated with
        :return: tuple with message and status code e.g. ("Maintenance state successfully
                 updated", 200)
        """
        log.info("Attempting to update maintenance mode state")
        try:
            _verify_token(access_token)
        except Exception as error:
            log.warning(f"Token was not valid: {access_token} - {error}")
            return "Access token was not valid", 403

        try:
            with open(MAINTENANCE_CONFIG_PATH, "w") as file:
                json.dump(state, file)
            log.info("Maintenance mode state successfully updated")
            return "Maintenance mode state successfully updated", 200
        except (FileNotFoundError, IOError, OverflowError, TypeError, ValueError):
            log.warning("Failed to update maintenance mode state")
            return "Failed to update maintenance mode state", 500


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

    def set_state(self, access_token, state):
        """
        Updates the scheduled maintenance mode state in the scheduled_maintenance.json file.
        :param access_token: the access token to be verified
        :param state: the state the JSON file to be updated with
        :return: tuple with message and status code e.g. ("Scheduled maintenance mode state
                 successfully updated", 200)
        """
        log.info("Attempting to update scheduled maintenance mode state")
        try:
            _verify_token(access_token)
        except Exception as error:
            log.warning(f"Token was not valid: {access_token} - {error}")
            return "Access token was not valid", 403

        try:
            with open(SCHEDULED_MAINTENANCE_CONFIG_PATH, "w") as file:
                json.dump(state, file)
            log.info("Scheduled maintenance mode state successfully updated")
            return "Scheduled maintenance mode state successfully updated", 200
        except (FileNotFoundError, IOError, OverflowError, TypeError, ValueError):
            log.warning("Failed to update scheduled maintenance mode state")
            return "Failed to update scheduled maintenance mode state", 500


def _verify_token(token):
    """
    Checks whether the token is valid and if it is in the blacklist.
    :param token: the token to be verified
    """
    log.info("Verifying token")
    jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    if token in BLACKLIST:
        log.warning(
            f"Token in blacklist: {token}")
        raise Exception("Token in blacklist")
    log.info("Token verified")
