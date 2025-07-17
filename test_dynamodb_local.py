import os
import boto3
from dotenv import load_dotenv
load_dotenv()

print("USE_DYNAMODB_LOCAL:", os.environ.get("USE_DYNAMODB_LOCAL"))
print("DYNAMODB_LOCAL_ENDPOINT:", os.environ.get("DYNAMODB_LOCAL_ENDPOINT"))

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.environ.get('DYNAMODB_LOCAL_ENDPOINT', 'http://localhost:8000'),
    region_name='us-west-2',
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey'
)
table = dynamodb.Table('Guests')
print(table.table_status)
