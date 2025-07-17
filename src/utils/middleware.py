import os
from utils.response import response, error_response
from utils.auth import verify_jwt
from aws_lambda_powertools import Logger

logger = Logger()

def cors_middleware(handler):
    def wrapper(event, context):
        result = handler(event, context)
        if isinstance(result, dict):
            headers = result.get('headers', {})
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            result['headers'] = headers
        return result
    return wrapper

def logging_middleware(handler):
    def wrapper(event, context):
        logger.info(f"Request: {event}")
        result = handler(event, context)
        logger.info(f"Response: {result}")
        return result
    return wrapper

def auth_middleware(handler):
    def wrapper(event, context):
        path = event.get('path', '')
        if not path.startswith('/health'):
            auth_header = event['headers'].get('Authorization')
            if not auth_header:
                return error_response(401, 'Missing Authorization header')
            token = auth_header.split(' ')[-1]
            try:
                verify_jwt(token)
            except Exception as e:
                return error_response(401, f'Invalid token: {e}')
        return handler(event, context)
    return wrapper

def compose_middleware(handler, middlewares):
    for mw in reversed(middlewares):
        handler = mw(handler)
    return handler
