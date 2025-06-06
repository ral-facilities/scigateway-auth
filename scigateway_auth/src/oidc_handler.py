import jwt
import requests

from scigateway_auth.common.config import OidcProviderConfig, config
from scigateway_auth.common.exceptions import InvalidJWTError


class OidcProvider:

    def __init__(self, config_url: str, audience: str, verify_cert: bool, mechanism: str, username_claim: str) -> None:
        self._audience = audience
        self._mechanism = mechanism
        self._username_claim = username_claim

        # Read discovery
        r = requests.get(config_url, verify=verify_cert)
        r.raise_for_status
        config = r.json()
        self._issuer = config["issuer"]

        # Read keys
        jwks_uri = config["jwks_uri"]
        r = requests.get(jwks_uri, verify=verify_cert)
        r.raise_for_status
        jwks_config = r.json()
        self._keys = {}
        for key in jwks_config["keys"]:
            kid = key["kid"]
            try:
                self._keys[kid] = jwt.PyJWK(key)
            except jwt.exceptions.PyJWKError:
                # Possibly unsupported algorithm (e.g. RSA-OAEP)
                pass

    def get_audience(self) -> str:
        return self._audience

    def get_issuer(self) -> str:
        return self._issuer

    def get_key(self, kid: str) -> jwt.PyJWK:
        return self._keys[kid]

    def get_mechanism(self) -> str:
        return self._mechanism

    def get_username_claim(self) -> str:
        return self._username_claim


class OidcHandler:

    def __init__(self) -> None:
        self._providers = {}
        for provider in config.authentication.oidc_providers.values():
            p = OidcProvider(provider.configuration_url, provider.audience, provider.verify_cert, provider.mechanism, provider.username_claim)
            self._providers[p.get_issuer()] = p

    def handle(self, encoded_token: str):
        try:
            unverified_header = jwt.get_unverified_header(encoded_token)
            unverified_payload = jwt.decode(encoded_token, options={'verify_signature': False})

            kid = unverified_header["kid"]
            iss = unverified_payload["iss"]
            provider = self._providers[iss]
            key = provider.get_key(kid)

            payload = jwt.decode(encoded_token, key=key, algorithms=[key.algorithm_name], audience=provider.get_audience(), options={"require": ["exp", "aud"], 'verify_exp': False, 'verify_aud': True})

            return (provider.get_mechanism(), payload[provider.get_username_claim()])

        except jwt.exceptions.InvalidTokenError as exc:
            raise InvalidJWTError("Invalid OIDC id token") from exc
