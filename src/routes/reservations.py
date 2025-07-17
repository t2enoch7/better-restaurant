import json
from utils.response import response, error_response
from services.reservation_service import ReservationService
from models.reservation import Reservation
from pydantic import ValidationError

def validate_request(model, data):
    try:
        return model(**data), None
    except ValidationError as e:
        return None, e.errors()

def handle_reservations(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    query = event.get('queryStringParameters') or {}
    body = json.loads(event.get('body', '{}')) if event.get('body') else {}
    last_evaluated_key = query.get('last_evaluated_key')
    limit = int(query.get('limit', 10))

    try:
        # /reservations
        if path == '/reservations' and method == 'POST':
            reservation_obj, errors = validate_request(Reservation, body)
            if errors:
                return error_response(400, {'validation': errors})
            reservation = ReservationService.create_reservation(reservation_obj.dict())
            return response(201, reservation)
        if path == '/reservations' and method == 'GET':
            reservations, lek = ReservationService.list_reservations(limit, json.loads(last_evaluated_key) if last_evaluated_key else None)
            pagination = {'last_evaluated_key': json.dumps(lek) if lek else None}
            return response(200, reservations, pagination=pagination)
        # /reservations/{reservation_id}
        if path.startswith('/reservations/'):
            parts = path.split('/')
            reservation_id = parts[2]
            if len(parts) == 3:
                if method == 'GET':
                    reservation = ReservationService.get_reservation(reservation_id)
                    if not reservation:
                        return error_response(404, 'Reservation not found')
                    return response(200, reservation)
                if method == 'PUT':
                    reservation_obj, errors = validate_request(Reservation, body)
                    if errors:
                        return error_response(400, {'validation': errors})
                    reservation = ReservationService.update_reservation(reservation_id, reservation_obj.dict())
                    return response(200, reservation)
                if method == 'DELETE':
                    ReservationService.delete_reservation(reservation_id)
                    return response(204)
            elif len(parts) == 4 and parts[3] == 'cancel' and method == 'POST':
                ReservationService.cancel_reservation(reservation_id)
                return response(200, {'message': 'Reservation cancelled'})
    except Exception as e:
        return error_response(500, str(e))
    return None
