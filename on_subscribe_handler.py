import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')


def handle(event, context):
    params = json.loads(event['body'])['params']
    connectionId = event['requestContext']['connectionId']

    apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', 
    endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    table = dynamodb.Table(os.environ['SOCKET_CHANNELS_TABLE_NAME'])

    table.put_item(Item={
        'id': str(uuid.uuid4()),
        'channelId': params['channel'],
        'connectionId': connectionId
    })
    apigatewaymanagementapi.post_to_connection(
        Data=json.dumps({
            'params': {
                'message': 'subscribed'
            }
        }),
        ConnectionId=connectionId
    )

    return {}