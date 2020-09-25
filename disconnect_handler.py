import json
import boto3
import os

dynamodb = boto3.client('dynamodb')

def handle(event, context):
    connectionId = event['requestContext']['connectionId']
    connectionIds = []

    # Delete connectionId from the database
    dynamodb.delete_item(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME'], Key={'connectionId': {'S': connectionId}})
    paginator = dynamodb.get_paginator('scan')
    operation_parameters = {
        'TableName': os.environ['SOCKET_CHANNELS_TABLE_NAME'],
        'FilterExpression': 'connectionId = :connectionId',
        'ExpressionAttributeValues': {
            ':connectionId': {'S': connectionId},
        }
    }

    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        connectionIds.extend(page['Items'])

    for res in connectionIds:
        dynamodb.delete_item(TableName=os.environ['SOCKET_CHANNELS_TABLE_NAME'], Key={'id': {'S': res['id']['S']}})

    return {}