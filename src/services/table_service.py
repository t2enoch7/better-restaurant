import os
import boto3
from models.table import Table
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
table = dynamodb.Table(os.environ['TABLES_TABLE'])

class TableService:
    @staticmethod
    def create_table(data: dict) -> dict:
        table_obj = Table(**data)
        table.put_item(Item=table_obj.dict())
        logger.info(f"Created table: {table_obj.table_id}")
        return table_obj.dict()

    @staticmethod
    def get_table(table_id: str) -> dict:
        resp = table.get_item(Key={'table_id': table_id})
        return resp.get('Item')

    @staticmethod
    def list_tables(limit=10, last_evaluated_key=None) -> (List[dict], Dict[str, Any]):
        scan_kwargs = {'Limit': limit}
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
        resp = table.scan(**scan_kwargs)
        return resp.get('Items', []), resp.get('LastEvaluatedKey')

    @staticmethod
    def update_table(table_id: str, data: dict) -> dict:
        table_obj = Table(**data)
        table.put_item(Item=table_obj.dict())
        logger.info(f"Updated table: {table_id}")
        return table_obj.dict()

    @staticmethod
    def delete_table(table_id: str):
        table.delete_item(Key={'table_id': table_id})
        logger.info(f"Deleted table: {table_id}")
