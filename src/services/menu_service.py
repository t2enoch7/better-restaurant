import os
import boto3
from models.menu import Menu
from aws_lambda_powertools import Logger
from typing import List, Dict, Any
from decimal import Decimal

logger = Logger()

def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    return obj

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
table = dynamodb.Table(os.environ['MENU_TABLE'])

class MenuService:
    @staticmethod
    def create_menu(data: dict) -> dict:
        menu = Menu(**data)
        item = convert_floats_to_decimal(menu.dict())
        table.put_item(Item=item)
        logger.info(f"Created menu: {menu.menu_id}")
        return item

    @staticmethod
    def get_menu(menu_id: str) -> dict:
        resp = table.get_item(Key={'menu_id': menu_id})
        return resp.get('Item')

    @staticmethod
    def list_menu(limit=10, last_evaluated_key=None) -> (List[dict], Dict[str, Any]):
        scan_kwargs = {'Limit': limit}
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
        resp = table.scan(**scan_kwargs)
        return resp.get('Items', []), resp.get('LastEvaluatedKey')

    @staticmethod
    def update_menu(menu_id: str, data: dict) -> dict:
        menu = Menu(**data)
        item = convert_floats_to_decimal(menu.dict())
        table.put_item(Item=item)
        logger.info(f"Updated menu: {menu_id}")
        return item

    @staticmethod
    def delete_menu(menu_id: str):
        table.delete_item(Key={'menu_id': menu_id})
        logger.info(f"Deleted menu: {menu_id}")
