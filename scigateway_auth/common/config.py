"""
Module for the overall configuration for the application.
"""

from pathlib import Path
from typing import List, Self

from pydantic import BaseModel, ConfigDict, HttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseModel):
    """
    Configuration model for the API.
    """

    root_path: str = ""  # (If using a proxy) The path prefix handled by a proxy that is not seen by the app.
    allowed_cors_headers: List[str]
    allowed_cors_origins: List[str]
    allowed_cors_methods: List[str]


class MaintenanceConfig(BaseModel):
    """
    Configuration model for maintenance
    """

    maintenance_path: str
    scheduled_maintenance_path: str


class OidcProviderConfig(BaseModel):
    """
    Configuration model for an OIDC provider
    """

    display_name: str
    configuration_url: HttpUrl
    client_id: str
    client_secret: str = None
    verify_cert: bool = True
    mechanism: str = None
    scope: str = "openid"
    username_claim: str = "sub"


class AuthenticationConfig(BaseModel):
    """
    Configuration model for the authentication.
    """

    private_key_path: str
    public_key_path: str
    jwt_algorithm: str
    access_token_validity_minutes: int
    refresh_token_validity_days: int
    jwt_refresh_token_blacklist: list[str]
    # These are the ICAT usernames of the users normally in the <icat-mnemonic>/<username> form
    admin_users: list[str]

    oidc_providers: dict[str, OidcProviderConfig] = {}
    oidc_redirect_url: HttpUrl = None
    oidc_icat_authenticator: str = None
    oidc_icat_authenticator_token: str = None

    @model_validator(mode="after")
    def validate_oidc(self) -> Self:
        if self.oidc_providers:
            if not self.oidc_icat_authenticator:
                raise ValueError("oidc_icat_authenticator is required if oidc_providers is set")
            if not self.oidc_icat_authenticator_token:
                raise ValueError("oidc_icat_authenticator_token is required if oidc_providers is set")
        return self


class ICATServerConfig(BaseModel):
    """
    Configuration model for the ICAT server.
    """

    url: str
    # The certificate validation corresponds to what is supplied to the `request` calls to the ICAT server.
    # `True` will verify certificates using its internal trust store.
    # `False` will disable certificate validation.
    certificate_validation: bool
    request_timeout_seconds: int

    model_config = ConfigDict(hide_input_in_errors=True)


class Config(BaseSettings):
    """
    Overall configuration model for the application.

    It includes attributes for the API, authentication, and LDAP server configurations. The class inherits from
    `BaseSettings` and automatically reads environment variables. If values are not passed in form of system environment
    variables at runtime, it will attempt to read them from the .env file.
    """

    api: APIConfig
    authentication: AuthenticationConfig
    icat_server: ICATServerConfig
    maintenance: MaintenanceConfig

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


config = Config()
