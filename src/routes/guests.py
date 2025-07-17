import json
from utils.response import response, error_response
from services.guest_service import GuestService
from models.guest import Guest
from pydantic import ValidationError

def validate_request(model, data):
    try:
        return model(**data), None
    except ValidationError as e:
        return None, e.errors()

def handle_guests(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    query = event.get('queryStringParameters') or {}
    body = json.loads(event.get('body', '{}')) if event.get('body') else {}
    last_evaluated_key = query.get('last_evaluated_key')
    limit = int(query.get('limit', 10))

    try:
        # /guests
        if path == '/guests' and method == 'POST':
            guest_obj, errors = validate_request(Guest, body)
            if errors:
                return error_response(400, {'validation': errors})
            guest = GuestService.create_guest(guest_obj.dict())
            return response(201, guest)
        if path == '/guests' and method == 'GET':
            guests, lek = GuestService.list_guests(limit, json.loads(last_evaluated_key) if last_evaluated_key else None)
            pagination = {'last_evaluated_key': json.dumps(lek) if lek else None}
            return response(200, guests, pagination=pagination)
        # /guests/{guest_id}
        if path.startswith('/guests/'):
            guest_id = path.split('/')[-1]
            if method == 'GET':
                guest = GuestService.get_guest(guest_id)
                if not guest:
                    return error_response(404, 'Guest not found')
                return response(200, guest)
            if method == 'PUT':
                guest_obj, errors = validate_request(Guest, body)
                if errors:
                    return error_response(400, {'validation': errors})
                guest = GuestService.update_guest(guest_id, guest_obj.dict())
                return response(200, guest)
            if method == 'DELETE':
                GuestService.delete_guest(guest_id)
                return response(204)
    except Exception as e:
        return error_response(500, str(e))
    return None
