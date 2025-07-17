import json
import os
from utils.response import response, error_response
from aws_lambda_powertools import Logger
from routes.guests import handle_guests
from routes.tables import handle_tables
from routes.menu import handle_menu
from routes.reservations import handle_reservations
from routes.dashboard import handle_dashboard
from utils.middleware import logging_middleware, cors_middleware, auth_middleware, compose_middleware

logger = Logger()

ROUTE_HANDLERS = [
    handle_guests,
    handle_tables,
    handle_menu,
    handle_reservations,
    handle_dashboard,
]

def _lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    path = event.get('path', '')
    try:
        # Dispatch to route handlers
        for handler in ROUTE_HANDLERS:
            result = handler(event, context)
            if result is not None:
                return result
        # Health check
        if path == '/health':
            return response(200, {'status': 'ok'})
        return error_response(404, 'Not found')
    except Exception as e:
        logger.error(f"Error: {e}")
        return error_response(500, str(e))

# Compose middleware: logging -> auth -> CORS
lambda_handler = compose_middleware(_lambda_handler, [logging_middleware, auth_middleware, cors_middleware])
