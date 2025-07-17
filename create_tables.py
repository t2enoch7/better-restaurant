import os
import boto3

def get_dynamodb():
    if os.environ.get('USE_DYNAMODB_LOCAL', 'false').lower() == 'true':
        return boto3.client(
            'dynamodb',
            endpoint_url=os.environ.get('DYNAMODB_LOCAL_ENDPOINT', 'http://localhost:8000'),
            region_name='us-west-2',
            aws_access_key_id='fakeMyKeyId',
            aws_secret_access_key='fakeSecretAccessKey'
        )
    return boto3.client('dynamodb')

def create_table(client, table_name, key_name):
    try:
        client.create_table(
            TableName=table_name,
            AttributeDefinitions=[{'AttributeName': key_name, 'AttributeType': 'S'}],
            KeySchema=[{'AttributeName': key_name, 'KeyType': 'HASH'}],
            BillingMode='PAY_PER_REQUEST',
        )
        print(f"Created table: {table_name}")
    except client.exceptions.ResourceInUseException:
        print(f"Table already exists: {table_name}")
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")

def main():
    client = get_dynamodb()
    tables = [
        ('Guests', 'guest_id'),
        ('Tables', 'table_id'),
        ('Menu', 'menu_id'),
        ('Reservations', 'reservation_id'),
    ]
    for table_name, key_name in tables:
        create_table(client, table_name, key_name)
    print("Done.")

if __name__ == "__main__":
    main()
