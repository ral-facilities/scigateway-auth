from cachetools.func import ttl_cache
import jwt
import requests

from scigateway_auth.common.config import config, OidcProviderConfig
from scigateway_auth.common.exceptions import InvalidJWTError, OidcProviderNotFoundError

# Amount of leeway (in seconds) when validating exp & iat
LEEWAY = 5

# Timeout for HTTP requests (in seconds)
TIMEOUT = 10


@ttl_cache(ttl=(24 * 60 * 60))
def get_well_known_config(provider_id: str) -> dict:

    try:
        provider_config: OidcProviderConfig = config.authentication.oidc_providers[provider_id]
    except KeyError:
        raise OidcProviderNotFoundError from None

    r = requests.get(provider_config.configuration_url, verify=provider_config.verify_cert, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


@ttl_cache(ttl=(2 * 60 * 60))
def get_jwks(provider_id: str) -> dict:

    try:
        provider_config: OidcProviderConfig = config.authentication.oidc_providers[provider_id]
    except KeyError:
        raise OidcProviderNotFoundError from None

    well_known_config = get_well_known_config(provider_id)
    jwks_uri = well_known_config["jwks_uri"]

    r = requests.get(jwks_uri, verify=provider_config.verify_cert, timeout=TIMEOUT)
    r.raise_for_status()
    jwks_config = r.json()

    keys = {}
    for key in jwks_config["keys"]:
        kid = key["kid"]
        try:
            keys[kid] = jwt.PyJWK(key)
        except jwt.exceptions.PyJWKError:
            # Possibly unsupported algorithm (e.g. RSA-OAEP)
            pass

    return keys


def get_token(provider_id: str, code: str) -> dict:

    try:
        provider_config: OidcProviderConfig = config.authentication.oidc_providers[provider_id]
    except KeyError:
        raise OidcProviderNotFoundError from None

    token_endpoint = get_well_known_config(provider_id)["token_endpoint"]

    r = requests.post(
        url=token_endpoint,
        data={
            "grant_type": "authorization_code",
            "client_id": provider_config.client_id,
            "client_secret": provider_config.client_secret,
            "code": code,
            "redirect_uri": config.authentication.oidc_redirect_uri,
        },
        verify=provider_config.verify_cert,
        timeout=TIMEOUT,
    )

    r.raise_for_status()
    return r.json()


def get_username(provider_id: str, id_token: str) -> tuple[str, str]:
    try:
        provider_config: OidcProviderConfig = config.authentication.oidc_providers[provider_id]
    except KeyError:
        raise OidcProviderNotFoundError from None

    try:
        unverified_header = jwt.get_unverified_header(id_token)

        try:
            kid = unverified_header["kid"]
            key = get_jwks(provider_id)[kid]
        except KeyError as exc:
            raise InvalidJWTError("Invalid OIDC id_token") from exc

        payload = jwt.decode(
            jwt=id_token,
            key=key,
            algorithms=[key.algorithm_name],
            audience=provider_config.client_id,
            issuer=get_well_known_config(provider_id)["issuer"],
            verify=True,
            options={"require": ["exp", "aud", "iss"], "verify_exp": True, "verify_aud": True, "verify_iss": True},
            leeway=LEEWAY,
        )

        try:
            username = payload[provider_config.username_claim]
        except KeyError:
            raise InvalidJWTError("Invalid OIDC id_token") from None

        return (provider_config.mechanism, username)

    except jwt.exceptions.InvalidTokenError as exc:
        raise InvalidJWTError("Invalid OIDC id_token") from exc
