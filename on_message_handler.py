import json
import boto3
import os

dynamodb = boto3.client('dynamodb')

USERINBOXSTATUSUPDATED = 'USERINBOXSTATUSUPDATED'
BROADCAST = 'BROADCAST'

def handle(event, context):
    params = json.loads(event['body'])['params']
    
    paginator = dynamodb.get_paginator('scan')
    
    connectionIds = []

    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Retrieve all connectionIds of channel from the database
    operation_parameters = {
        'TableName': os.environ['SOCKET_CHANNELS_TABLE_NAME'],
        'FilterExpression': 'channelId = :channelId',
        'ExpressionAttributeValues': {
            ':channelId': {'S': params['channel']},
        }
    }

    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        connectionIds.extend(page['Items'])

    # Emit the recieved message to all the connected devices
    for connectionId in connectionIds:
        if params['event'] == USERINBOXSTATUSUPDATED:
            apigatewaymanagementapi.post_to_connection(
                Data=json.dumps({
                    'event': params['event'],
                    'count': params['count'],
                    'channel': params['channel'],
                }),
                ConnectionId=connectionId['connectionId']['S']
            )
        else:
            apigatewaymanagementapi.post_to_connection(
                Data=json.dumps({
                    'event': params['event'],
                    'content': params['content'],
                    'channel': params['channel'],
                }),
                ConnectionId=connectionId['connectionId']['S']
            )

    return {}