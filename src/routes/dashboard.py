from utils.response import response
from services.reservation_service import ReservationService

def handle_dashboard(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    if path.startswith('/dashboard/') and method == 'GET':
        guest_id = path.split('/')[-1]
        dashboard = ReservationService.get_dashboard_for_guest(guest_id)
        return response(200, dashboard)
    return None
