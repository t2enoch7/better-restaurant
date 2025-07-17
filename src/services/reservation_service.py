import os
import boto3
from models.reservation import Reservation
from aws_lambda_powertools import Logger
from typing import List, Dict, Any

logger = Logger()

def get_dynamodb_resource():
    if os.environ.get('USE_DYNAMODB_LOCAL') == 'true':
        return boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('DYNAMODB_LOCAL_ENDPOINT', 'http://localhost:8000'),
            region_name='us-west-2',
            aws_access_key_id='fakeMyKeyId',
            aws_secret_access_key='fakeSecretAccessKey'
        )
    return boto3.resource('dynamodb')

dynamodb = get_dynamodb_resource()
table = dynamodb.Table(os.environ['RESERVATIONS_TABLE'])

guest_table = dynamodb.Table(os.environ['GUESTS_TABLE'])
table_table = dynamodb.Table(os.environ['TABLES_TABLE'])
menu_table = dynamodb.Table(os.environ['MENU_TABLE'])

class ReservationService:
    @staticmethod
    def create_reservation(data: dict) -> dict:
        reservation = Reservation(**data)
        table.put_item(Item=reservation.dict())
        logger.info(f"Created reservation: {reservation.reservation_id}")
        return reservation.dict()

    @staticmethod
    def get_reservation(reservation_id: str) -> dict:
        resp = table.get_item(Key={'reservation_id': reservation_id})
        return resp.get('Item')

    @staticmethod
    def list_reservations(limit=10, last_evaluated_key=None) -> (List[dict], Dict[str, Any]):
        scan_kwargs = {'Limit': limit}
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
        resp = table.scan(**scan_kwargs)
        return resp.get('Items', []), resp.get('LastEvaluatedKey')

    @staticmethod
    def update_reservation(reservation_id: str, data: dict) -> dict:
        reservation = Reservation(**data)
        table.put_item(Item=reservation.dict())
        logger.info(f"Updated reservation: {reservation_id}")
        return reservation.dict()

    @staticmethod
    def delete_reservation(reservation_id: str):
        table.delete_item(Key={'reservation_id': reservation_id})
        logger.info(f"Deleted reservation: {reservation_id}")

    @staticmethod
    def cancel_reservation(reservation_id: str):
        table.update_item(
            Key={'reservation_id': reservation_id},
            UpdateExpression="set #s = :c",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':c': 'cancelled'}
        )
        logger.info(f"Cancelled reservation: {reservation_id}")

    @staticmethod
    def get_dashboard_for_guest(guest_id: str) -> dict:
        # Get guest
        guest = guest_table.get_item(Key={'guest_id': guest_id}).get('Item')
        # Get reservations
        reservations = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('guest_id').eq(guest_id)).get('Items', [])
        # Get tables and menu for each reservation
        dashboard = {
            'guest': guest,
            'reservations': []
        }
        for r in reservations:
            table_info = table_table.get_item(Key={'table_id': r['table_id']}).get('Item')
            menu_info = menu_table.get_item(Key={'menu_id': r['menu_id']}).get('Item')
            dashboard['reservations'].append({
                'reservation': r,
                'table': table_info,
                'menu': menu_info
            })
        return dashboard
