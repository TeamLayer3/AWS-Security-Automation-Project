import os, time, boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONNECTIONS_TABLE'])

def lambda_handler(event, context):
    conn_id = event['requestContext']['connectionId']

    # 선택: 쿼리스트링/헤더에서 메타데이터 받기
    qs = event.get('queryStringParameters') or {}
    client_id = qs.get('clientId') or 'unknown'
    account = qs.get('account')
    region  = qs.get('region')

    item = {
        'connectionId': conn_id,
        'createdAt': int(time.time() * 1000)  # ms (Node.js Date.now()와 동일)
    }
    # 선택 속성
    if client_id: item['clientId'] = client_id
    if account:   item['account']   = account
    if region:    item['region']    = region

    table.put_item(Item=item)
    return {'statusCode': 200, 'body': 'connected'}
