"""
Module for providing an API router which defines the maintenance routes.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from scigateway_auth.common.exceptions import (
    InvalidJWTError,
    InvalidMaintenanceFileError,
    MaintenanceFileReadError,
    MaintenanceFileWriteError,
    UserNotAdminError,
)
from scigateway_auth.common.schemas import (
    MaintenancePutRequestSchema,
    MaintenanceStateSchema,
    ScheduledMaintenancePutRequestSchema,
    ScheduledMaintenanceStateSchema,
)
from scigateway_auth.src.jwt_handler import JWTHandler
from scigateway_auth.src.maintenance import MaintenanceMode, ScheduledMaintenanceMode

logger = logging.getLogger()

router = APIRouter(tags=["maintenance"])

MaintenanceModeDep = Annotated[MaintenanceMode, Depends(MaintenanceMode)]

ScheduledMaintenanceModeDep = Annotated[ScheduledMaintenanceMode, Depends(ScheduledMaintenanceMode)]


def _verify_user_is_admin(access_token: str) -> None:
    """
    Verify the user's JWT access token is valid and ensure they are an admin.

    :param access_token: The user's JWT access token.
    """
    jwt_handler = JWTHandler()
    payload = jwt_handler.verify_token(access_token)
    if "userIsAdmin" not in payload or not payload["userIsAdmin"]:
        raise UserNotAdminError("Maintenance state update attempted by non-admin user")


@router.get(
    path="/maintenance",
    summary="Get the maintenance state",
    response_description="Returns the maintenance state",
)
def get_maintenance_state(maintenance_mode: MaintenanceModeDep) -> MaintenanceStateSchema:
    logger.info("Getting maintenance state")
    try:
        return maintenance_mode.get_maintenance_state()
    except (InvalidMaintenanceFileError, MaintenanceFileReadError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get maintenance state",
        ) from exc


@router.put(
    path="/maintenance",
    summary="Update the maintenance state",
    response_description="200 status code (no response body) if the maintenance state was successfully updated",
)
def update_maintenance_state(
    maintenance_mode: MaintenanceModeDep,
    maintenance: MaintenancePutRequestSchema,
) -> Response:
    logger.info("Updating maintenance state")
    try:
        _verify_user_is_admin(maintenance.token)
        maintenance_mode.update_maintenance_state(maintenance.maintenance)
        return Response(status_code=status.HTTP_200_OK)
    except (InvalidJWTError, UserNotAdminError) as exc:
        message = "Unable to update maintenance state"
        logger.exception(message)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message) from exc
    except MaintenanceFileWriteError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update maintenance state",
        ) from exc


@router.get(
    path="/scheduled_maintenance",
    summary="Get the scheduled maintenance state",
    response_description="Returns the scheduled maintenance state",
)
def get_scheduled_maintenance_state(
    scheduled_maintenance_mode: ScheduledMaintenanceModeDep,
) -> ScheduledMaintenanceStateSchema:
    logger.info("Getting scheduled maintenance state")
    try:
        return scheduled_maintenance_mode.get_maintenance_state()
    except (InvalidMaintenanceFileError, MaintenanceFileReadError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheduled maintenance state",
        ) from exc


@router.put(
    path="/scheduled_maintenance",
    summary="Update the scheduled maintenance state",
    response_description="200 status code (no response body) if the scheduled maintenance was successfully updated",
)
def update_scheduled_maintenance_state(
    scheduled_maintenance_mode: ScheduledMaintenanceModeDep,
    scheduled_maintenance: ScheduledMaintenancePutRequestSchema,
) -> Response:
    logger.info("Updating scheduled maintenance state")
    try:
        _verify_user_is_admin(scheduled_maintenance.token)
        scheduled_maintenance_mode.update_maintenance_state(scheduled_maintenance.scheduled_maintenance)
        return Response(status_code=status.HTTP_200_OK)
    except (InvalidJWTError, UserNotAdminError) as exc:
        message = "Unable to update scheduled maintenance state"
        logger.exception(message)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message) from exc
    except MaintenanceFileWriteError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update scheduled maintenance state",
        ) from exc
