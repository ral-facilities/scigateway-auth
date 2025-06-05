"""
Model for defining the API schema models.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class UserCredentialsPostRequestSchema(BaseModel):
    """
    Schema model for the user credentials within a login `POST` request.
    """

    username: SecretStr = Field(description="The user's username")
    password: SecretStr = Field(description="The user's password")

    model_config = ConfigDict(hide_input_in_errors=True)


class LoginDetailsPostRequestSchema(BaseModel):
    """
    Schema model for a login `POST` request.
    """

    mnemonic: str = Field(description="The ICAT mnemonic")
    credentials: Optional[UserCredentialsPostRequestSchema] = Field(default=None, description="The ICAT credentials")


class MaintenanceStateSchema(BaseModel):
    """
    Schema model for the maintenance state.
    """

    show: bool = Field(description="Whether the maintenance message should be shown")
    message: str = Field(description="The maintenance message to be shown")


class MaintenancePutRequestSchema(BaseModel):
    """
    Schema model for a maintenance `PUT` request.
    """

    token: str = Field(description="The user's access token")
    maintenance: MaintenanceStateSchema = Field(description="The maintenance state")


class ScheduledMaintenanceStateSchema(MaintenanceStateSchema):
    """
    Schema model for the scheduled maintenance state.
    """

    severity: str = Field(description="The severity of the maintenance")


class ScheduledMaintenancePutRequestSchema(BaseModel):
    """
    Schema model for a scheduled maintenance `PUT` request.
    """

    token: str = Field(description="The user's access token")
    scheduled_maintenance: ScheduledMaintenanceStateSchema = Field(
        alias="scheduledMaintenance",
        description="The scheduled maintenance state",
    )
