"""
Module for providing an API router which defines the authentication routes.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from scigateway_auth.common.config import config
from scigateway_auth.common.exceptions import (
    BlacklistedJWTError,
    ICATAuthenticationError,
    InvalidJWTError,
    JWTRefreshError,
    OidcProviderNotFoundError,
    UsernameMismatchError,
)
from scigateway_auth.common.schemas import LoginDetailsPostRequestSchema
from scigateway_auth.src import oidc
from scigateway_auth.src.authentication import ICATAuthenticator
from scigateway_auth.src.jwt_handler import JWTHandler

logger = logging.getLogger()

router = APIRouter(tags=["authentication"])

JWTHandlerDep = Annotated[JWTHandler, Depends(JWTHandler)]


@router.get(
    path="/authenticators",
    summary="Get a list of valid ICAT authenticators",
    response_description="Returns a list of valid ICAT authenticators",
)
def get_authenticators():
    logger.info("Getting a list of valid ICAT authenticators")
    try:
        return ICATAuthenticator.get_authenticators()
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve authenticators",
        ) from exc


@router.get(
    path="/oidc_providers",
    summary="Get a list of OIDC providers",
    response_description="Returns a list of OIDC providers",
)
def get_oidc_providers() -> JSONResponse:
    logger.info("Getting a list of OIDC providers")

    providers = {}
    for provider_id, provider_config in config.authentication.oidc_providers.items():
        providers[provider_id] = {
            "display_name": provider_config.display_name,
            "configuration_url": provider_config.configuration_url,
            "client_id": provider_config.client_id,
            "pkce": False if provider_config.client_secret else True,
            "scope": provider_config.scope,
        }

    return JSONResponse(content=providers)


@router.post(
    path="/login",
    summary="Login with ICAT mnemonic and credentials",
    response_description="A JWT access token including a refresh token as an HTTP-only cookie",
)
def login(
    jwt_handler: JWTHandlerDep,
    login_details: Annotated[
        LoginDetailsPostRequestSchema,
        Body(description="The ICAT mnemonic and credentials to be used to login and obtain a session"),
    ],
) -> JSONResponse:
    logger.info("Authenticating a user")
    try:
        if login_details.credentials is not None:
            credentials = {
                "username": login_details.credentials.username.get_secret_value(),
                "password": login_details.credentials.password.get_secret_value(),
            }
        else:
            credentials = None

        icat_session_id = ICATAuthenticator.authenticate(login_details.mnemonic, credentials)
        icat_username = ICATAuthenticator.get_username(icat_session_id)

        access_token = jwt_handler.get_access_token(icat_session_id, icat_username)
        refresh_token = jwt_handler.get_refresh_token(icat_username)

        response = JSONResponse(content=access_token)
        response.set_cookie(
            key="scigateway:refresh_token",
            value=refresh_token,
            max_age=config.authentication.refresh_token_validity_days * 24 * 60 * 60,
            secure=True,
            httponly=True,
            samesite="lax",
            path=f"{config.api.root_path}/refresh",
        )
        return response
    except ICATAuthenticationError as exc:
        logger.exception(exc.args)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post(
    path="/oidc_token/{provider_id}",
    summary="Get an OIDC id_token",
    response_description="OIDC token endpoint response",
)
def oidc_token(
    provider_id: Annotated[str, "OIDC provider id"],
    code: Annotated[str, Body(description="OIDC authorization code")],
) -> JSONResponse:
    logger.info("Obtaining an id_token")

    try:
        token_response = oidc.get_token(provider_id, code)
    except OidcProviderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown OIDC provider: " + provider_id,
        ) from None

    return JSONResponse(content=token_response)


@router.post(
    path="/oidc_login/{provider_id}",
    summary="Login with an OIDC id token",
    response_description="A JWT access token including a refresh token as an HTTP-only cookie",
)
def oidc_login(
    jwt_handler: JWTHandlerDep,
    provider_id: Annotated[str, "The OIDC provider id"],
    bearer_token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer(description="OIDC id token"))],
) -> JSONResponse:
    logger.info("Authenticating a user")

    id_token = bearer_token.credentials

    try:
        mechanism, oidc_username = oidc.get_username(provider_id, id_token)
    except OidcProviderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown OIDC provider: " + provider_id,
        ) from None
    except InvalidJWTError as exc:
        logger.exception(exc.args)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    credentials = {
        "mechanism": mechanism,
        "username": oidc_username,
        "token": config.authentication.oidc_icat_authenticator_token,
    }

    try:
        icat_session_id = ICATAuthenticator.authenticate(config.authentication.oidc_icat_authenticator, credentials)
        icat_username = ICATAuthenticator.get_username(icat_session_id)

        access_token = jwt_handler.get_access_token(icat_session_id, icat_username)
        refresh_token = jwt_handler.get_refresh_token(icat_username)

        response = JSONResponse(content=access_token)
        response.set_cookie(
            key="scigateway:refresh_token",
            value=refresh_token,
            max_age=config.authentication.refresh_token_validity_days * 24 * 60 * 60,
            secure=True,
            httponly=True,
            samesite="lax",
            path=f"{config.api.root_path}/refresh",
        )
        return response
    except ICATAuthenticationError as exc:
        logger.exception(exc.args)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post(
    path="/refresh",
    summary="Generate an updated JWT access token using the JWT refresh token",
    response_description="A JWT access token",
)
def refresh_access_token(
    jwt_handler: JWTHandlerDep,
    token: Annotated[str, Body(description="The JWT access token to refresh", embed=True)],
    refresh_token: Annotated[
        str | None,
        Cookie(alias="scigateway:refresh_token", description="The JWT refresh token from an HTTP-only cookie"),
    ] = None,
) -> JSONResponse:
    logger.info("Refreshing a JWT access token")
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No JWT refresh token found")

    try:
        access_token = jwt_handler.refresh_access_token(token, refresh_token)
        return JSONResponse(content=access_token)
    except (BlacklistedJWTError, InvalidJWTError, JWTRefreshError, UsernameMismatchError) as exc:
        message = "Unable to refresh access token"
        logger.exception(message)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message) from exc


@router.post(
    path="/verify",
    summary="Verify that a JWT token was generated by this authentication service",
    response_description="200 status code (no response body) if the token is valid",
)
def verify_token(
    jwt_handler: JWTHandlerDep,
    token: Annotated[str, Body(description="The JWT token to verify", embed=True)],
) -> Response:
    logger.info("Verifying a JWT token")
    try:
        jwt_handler.verify_token(token)
        return Response(status_code=status.HTTP_200_OK)
    except InvalidJWTError as exc:
        message = "Invalid JWT token provided"
        logger.exception(message)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message) from exc
