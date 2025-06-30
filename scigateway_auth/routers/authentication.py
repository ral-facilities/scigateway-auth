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
    UsernameMismatchError,
)
from scigateway_auth.common.schemas import LoginDetailsPostRequestSchema
from scigateway_auth.src.authentication import ICATAuthenticator, OIDC_ICATAuthenticator
from scigateway_auth.src.jwt_handler import JWTHandler
from scigateway_auth.src.oidc_handler import OidcHandler

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
def get_oidc_providers():
    logger.info("Getting a list of OIDC prociders")

    return [ {"display_name": p.display_name, "configuration_url": p.configuration_url, "client_id": p.client_id } for p in config.authentication.oidc_providers.values() ]


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
        icat_session_id = ICATAuthenticator.authenticate(login_details.mnemonic, login_details.credentials)
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
    path="/oidc_login",
    summary="Login with an OIDC id token",
    response_description="A JWT access token including a refresh token as an HTTP-only cookie",
)
def oidc_login(
    jwt_handler: JWTHandlerDep,
    oidc_handler: Annotated[OidcHandler, Depends(OidcHandler)],
    bearer_token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer(description="OIDC id token"))]
) -> JSONResponse:
    logger.info("Authenticating a user")

    encoded_token = bearer_token.credentials

    try:
        mechanism, oidc_username = oidc_handler.handle(encoded_token)
    except InvalidJWTError as exc:
        logger.exception(exc.args)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    try:
        icat_session_id = OIDC_ICATAuthenticator.authenticate(mechanism, oidc_username)
        icat_username = OIDC_ICATAuthenticator.get_username(icat_session_id)

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
