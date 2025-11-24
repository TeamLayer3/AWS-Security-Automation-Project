import os, boto3, json, time

EVENT_DDB_TABLE = os.environ['EVENT_CONNECTIONS_TABLE']
REMED_DDB_TABLE = os.environ['REMED_CONNECTIONS_TABLE']
EVENT_ENDPOINT = os.environ['EVENT_API_GW_ENDPOINT']
REMED_ENDPOINT = os.environ['REMED_API_GW_ENDPOINT']
HISTORY_DDB_TABLE = os.environ['HISTORY_CONNECTIONS_TABLE']
HISTORY_ENDPOINT = os.environ['HISTORY_API_GW_ENDPOINT']

dynamodb = boto3.resource('dynamodb')

def send_ping(connection_id, endpoint):
    apigw_management = boto3.client('apigatewaymanagementapi', endpoint_url=f"https://{endpoint}")
    try:
        apigw_management.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({"type": "ping", "timestamp": int(time.time() * 1000)})
        )
        print(f"Ping sent to {connection_id} via {endpoint}")
        return True
    except apigw_management.exceptions.GoneException:
        print(f"Connection {connection_id} is gone on {endpoint}")
        return False 
    except Exception as e:
        print(f"Error sending to {connection_id} on {endpoint}: {e}")
        return False 

def get_connections_and_ping(table_name, endpoint):
    table = dynamodb.Table(table_name)
    response = table.scan(ProjectionExpression='connectionId')
    connection_ids = [item['connectionId'] for item in response.get('Items', [])]
    
    successful_pings = 0
    for connection_id in connection_ids:
        if send_ping(connection_id, endpoint):
            successful_pings += 1
        else:
            try: table.delete_item(Key={'connectionId': connection_id})
            except: pass
            
    return successful_pings

def lambda_handler(event, context):
    event_count = get_connections_and_ping(EVENT_DDB_TABLE, EVENT_ENDPOINT)
 
    remed_count = get_connections_and_ping(REMED_DDB_TABLE, REMED_ENDPOINT)

    history_count = get_connections_and_ping(HISTORY_DDB_TABLE, HISTORY_ENDPOINT)
    
    return {
        'statusCode': 200,
        'body': f"Event Pinged: {event_count}, Remed Pinged: {remed_count}, History Pinged: {history_count}"
    }
