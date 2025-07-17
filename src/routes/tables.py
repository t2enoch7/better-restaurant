import json
from utils.response import response, error_response
from services.table_service import TableService
from services.reservation_service import ReservationService
from models.table import Table
from pydantic import ValidationError

def validate_request(model, data):
    try:
        return model(**data), None
    except ValidationError as e:
        return None, e.errors()

def handle_tables(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    query = event.get('queryStringParameters') or {}
    body = json.loads(event.get('body', '{}')) if event.get('body') else {}
    last_evaluated_key = query.get('last_evaluated_key')
    limit = int(query.get('limit', 10))

    try:
        # /tables
        if path == '/tables' and method == 'POST':
            table_obj, errors = validate_request(Table, body)
            if errors:
                return error_response(400, {'validation': errors})
            table = TableService.create_table(table_obj.dict())
            return response(201, table)
        if path == '/tables' and method == 'GET':
            tables, lek = TableService.list_tables(limit, json.loads(last_evaluated_key) if last_evaluated_key else None)
            pagination = {'last_evaluated_key': json.dumps(lek) if lek else None}
            return response(200, tables, pagination=pagination)
        # /tables/{table_id}
        if path.startswith('/tables/') and path != '/tables/reserved':
            table_id = path.split('/')[-1]
            if method == 'GET':
                table = TableService.get_table(table_id)
                if not table:
                    return error_response(404, 'Table not found')
                return response(200, table)
            if method == 'PUT':
                table_obj, errors = validate_request(Table, body)
                if errors:
                    return error_response(400, {'validation': errors})
                table = TableService.update_table(table_id, table_obj.dict())
                return response(200, table)
            if method == 'DELETE':
                TableService.delete_table(table_id)
                return response(204)
        # /tables/reserved
        if path == '/tables/reserved' and method == 'GET':
            # Get all reservations, extract reserved table_ids, then fetch those tables
            reservations, _ = ReservationService.list_reservations(limit=1000)  # adjust limit as needed
            reserved_table_ids = {r['table_id'] for r in reservations if r.get('status', 'active') == 'active'}
            all_tables, _ = TableService.list_tables(limit=1000)
            reserved_tables = [t for t in all_tables if t['table_id'] in reserved_table_ids]
            return response(200, reserved_tables)
    except Exception as e:
        return error_response(500, str(e))
    return None
