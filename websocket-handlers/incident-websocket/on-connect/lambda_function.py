# file: history_connect.py
import os, time, boto3
from botocore.exceptions import ClientError

CONNECTIONS_TABLE = os.environ["CONNECTIONS_TABLE"]
TTL_HOURS = int(os.getenv("TTL_HOURS", "24"))

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(CONNECTIONS_TABLE)

def lambda_handler(event, context):
    cid = event["requestContext"]["connectionId"]
    qs = event.get("queryStringParameters") or {}
    client_id = (qs.get("clientId") or "unknown").strip()
    account   = (qs.get("account") or "").strip()
    region    = (qs.get("region") or "").strip()

    now_sec = int(time.time())
    item = {
        "connectionId": cid,
        "createdAt": now_sec * 1000,
        "ttl": now_sec + TTL_HOURS * 3600,
        "clientId": client_id,
    }
    if account: item["account"] = account
    if region:  item["region"]  = region

    try:
        table.put_item(Item=item)
    except ClientError as e:
        print("put_item error:", e)
        return {"statusCode": 500, "body": "DB error"}

    return {"statusCode": 200, "body": "connected"}
