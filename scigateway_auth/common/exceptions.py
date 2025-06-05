"""
Module for custom exception classes.
"""


class BlacklistedJWTError(Exception):
    """
    Exception raised when blacklisted JWT token is provided.
    """


class ICATAuthenticationError(Exception):
    """
    Exception raised when there are ICAT authentication related errors/issues.
    """


class InvalidJWTError(Exception):
    """
    Exception raised when invalid JWT token is provided.
    """


class InvalidMaintenanceFileError(Exception):
    """
    Exception raised when the maintenance state file does not have the correct format or value types.
    """


class JWTRefreshError(Exception):
    """
    Exception raised when JWT access token cannot be refreshed.
    """


class MaintenanceFileReadError(Exception):
    """
    Exception raised when the maintenance state file's data cannot be read.
    """


class MaintenanceFileWriteError(Exception):
    """
    Exception raised when the maintenance state cannot be written to the file.
    """


class UsernameMismatchError(Exception):
    """
    Exception raised when the usernames in the access and refresh tokens do not match.
    """


class UserNotAdminError(Exception):
    """
    Exception raised when a non-admin user performs an action that requires the user to be an admin.
    """
