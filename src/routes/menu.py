import json
from utils.response import response, error_response
from services.menu_service import MenuService
from models.menu import Menu
from pydantic import ValidationError

def validate_request(model, data):
    try:
        return model(**data), None
    except ValidationError as e:
        return None, e.errors()

def handle_menu(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    query = event.get('queryStringParameters') or {}
    body = json.loads(event.get('body', '{}')) if event.get('body') else {}
    last_evaluated_key = query.get('last_evaluated_key')
    limit = int(query.get('limit', 10))

    try:
        # /menu
        if path == '/menu' and method == 'POST':
            menu_obj, errors = validate_request(Menu, body)
            if errors:
                return error_response(400, {'validation': errors})
            menu = MenuService.create_menu(menu_obj.dict())
            return response(201, menu)
        if path == '/menu' and method == 'GET':
            menu, lek = MenuService.list_menu(limit, json.loads(last_evaluated_key) if last_evaluated_key else None)
            pagination = {'last_evaluated_key': json.dumps(lek) if lek else None}
            return response(200, menu, pagination=pagination)
        # /menu/{menu_id}
        if path.startswith('/menu/'):
            menu_id = path.split('/')[-1]
            if method == 'GET':
                menu = MenuService.get_menu(menu_id)
                if not menu:
                    return error_response(404, 'Menu item not found')
                return response(200, menu)
            if method == 'PUT':
                menu_obj, errors = validate_request(Menu, body)
                if errors:
                    return error_response(400, {'validation': errors})
                menu = MenuService.update_menu(menu_id, menu_obj.dict())
                return response(200, menu)
            if method == 'DELETE':
                MenuService.delete_menu(menu_id)
                return response(204)
    except Exception as e:
        return error_response(500, str(e))
    return None
