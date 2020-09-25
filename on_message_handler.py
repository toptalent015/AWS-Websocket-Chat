import json
import boto3
import os

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    action = json.loads(event['body'])['action']
    params = json.loads(event['body'])['params']
    
    paginator = dynamodb.get_paginator('scan')
    
    connectionIds = []

    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Retrieve all connectionIds from the database
    for page in paginator.paginate(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME']):
        connectionIds.extend(page['Items'])

    # Emit the recieved message to all the connected devices
    for connectionId in connectionIds:
        apigatewaymanagementapi.post_to_connection(
            Data=json.dumps({
                'params': params,
                'action': action
            }),
            ConnectionId=connectionId['connectionId']['S']
        )

    return {}