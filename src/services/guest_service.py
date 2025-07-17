import os
import boto3
from boto3.dynamodb.conditions import Key
from models.guest import Guest
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
table = dynamodb.Table(os.environ['GUESTS_TABLE'])

class GuestService:
    @staticmethod
    def create_guest(data: dict) -> dict:
        guest = Guest(**data)
        table.put_item(Item=guest.dict())
        logger.info(f"Created guest: {guest.guest_id}")
        return guest.dict()

    @staticmethod
    def get_guest(guest_id: str) -> dict:
        resp = table.get_item(Key={'guest_id': guest_id})
        return resp.get('Item')

    @staticmethod
    def list_guests(limit=10, last_evaluated_key=None) -> (List[dict], Dict[str, Any]):
        scan_kwargs = {'Limit': limit}
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
        resp = table.scan(**scan_kwargs)
        return resp.get('Items', []), resp.get('LastEvaluatedKey')

    @staticmethod
    def update_guest(guest_id: str, data: dict) -> dict:
        guest = Guest(**data)
        table.put_item(Item=guest.dict())
        logger.info(f"Updated guest: {guest_id}")
        return guest.dict()

    @staticmethod
    def delete_guest(guest_id: str):
        table.delete_item(Key={'guest_id': guest_id})
        logger.info(f"Deleted guest: {guest_id}")
