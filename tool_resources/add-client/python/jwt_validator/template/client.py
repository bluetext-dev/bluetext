import jwt
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

#### Types ####

class JwtValidatorConfig(BaseModel):
    """Configuration for the JWT validator."""
    # The JWK URL to fetch keys from.
    jwk_url: str | None = None
    # The audience for the JWTs.
    audience: str | list[str] | None = None
    # Allowed signing algorithms for JWTs
    algorithms: set[str] | None = set(["ES256", "EdDSA", "RS256", "HS256"])
    # Optional leeway for the expiration check, to allow for clock skew (in seconds)
    leeway: float = 0

#### Client ####

def get_jwk_client(jwk_url: str):
    """Creates a JWK client for the configured JWK URL."""
    return jwt.PyJWKClient(jwk_url)

class JwtValidator():
    """Simple JWT validator. Supports """

    def __init__(self, config: JwtValidatorConfig):
        self.config = JwtValidatorConfig(**config.dict())
        self.decode_options = {}
        if self.config.jwk_url:
            self.client = get_jwk_client(self.config.jwk_url)
        else:
            logger.warning("No JWK URL configured - will _NOT_ verify JWT signatures")
            self.decode_options["verify_signature"] = False
        if not self.config.algorithms:
            logger.warning(
                "No algorithms configured - will allow _ANY_ JWT signing algorithm"
            )
        if not self.config.audience:
            logger.warning("No audience configured - will _NOT_ verify JWT audience")
            self.decode_options["verify_aud"] = False
        if self.config.leeway and self.config.leeway > 0:
            if self.config.leeway > 1:
                logger.warning(f"Running with large JWT leeway ({self.config.leeway}s)")
            else:
                logger.info(f"Running with JWT leeway ({self.config.leeway}s)")

    def decode_jwt(self, token: str) -> dict | None:
        "Decodes a JWT using the configured JWKS URL and audience."
        try:
            if self.client:
                signing_key = self.client.get_signing_key_from_jwt(token)
            else:
                signing_key = None
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=self.config.algorithms,
                audience=self.config.audience,
                options=self.decode_options,
            )
        except Exception as e:
            # TODO: enumerate the exceptions thrown by PyJWT and map to own exceptions
            try:
                debug_payload = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
                logger.warning(f"JWT validation error: {e}. Token claims: {debug_payload}")
            except Exception as debug_e:
                logger.warning(f"JWT validation error: {e}. Could not decode token for debug: {debug_e}")