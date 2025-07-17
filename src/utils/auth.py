import os
import requests
from jose import jwt
from jose.exceptions import JWTError
from aws_lambda_powertools import Logger

logger = Logger()

COGNITO_REGION = os.environ.get("AWS_REGION", "us-east-1")
USERPOOL_ID = os.environ.get("COGNITO_USERPOOL_ID")
APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")

JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USERPOOL_ID}/.well-known/jwks.json"
_jwks = None

def get_jwks():
    global _jwks
    if _jwks is None:
        resp = requests.get(JWKS_URL)
        resp.raise_for_status()
        _jwks = resp.json()["keys"]
    return _jwks

def verify_jwt(token):
    # Mock mode for local testing
    if os.environ.get('MOCK_COGNITO_JWT', 'false').lower() == 'true':
        logger.info("MOCK_COGNITO_JWT enabled: returning mock claims.")
        return {
            'sub': 'mock-user-id',
            'email': 'mockuser@example.com',
            'cognito:username': 'mockuser',
            'scope': 'user',
            'iss': 'mock-issuer',
            'aud': APP_CLIENT_ID or 'mock-client-id',
        }
    try:
        jwks = get_jwks()
        header = jwt.get_unverified_header(token)
        key = next(k for k in jwks if k["kid"] == header["kid"])
        claims = jwt.decode(token, key, algorithms=[header["alg"]], audience=APP_CLIENT_ID)
        logger.info(f"JWT verified for sub: {claims.get('sub')}")
        return claims
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise
