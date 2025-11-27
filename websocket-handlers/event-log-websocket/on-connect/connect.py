# file: events_connect.py
import os
import time
import boto3
from botocore.exceptions import ClientError

CONNECTIONS_TABLE = os.environ["CONNECTIONS_TABLE"]
TTL_HOURS = int(os.getenv("TTL_HOURS", "24"))

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(CONNECTIONS_TABLE)

def _extract_source_ip(event) -> str:
    # 우선순위 1: requestContext.identity.sourceIp
    rc = event.get("requestContext") or {}
    identity = rc.get("identity") or {}
    ip = (identity.get("sourceIp") or "").strip()
    if ip:
        return ip
    # 우선순위 2: X-Forwarded-For (첫 번째 IP)
    headers = event.get("headers") or {}
    xff = (headers.get("X-Forwarded-For") or headers.get("x-forwarded-for") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    return ""

def lambda_handler(event, context):
    rc = event.get("requestContext") or {}
    cid = (rc.get("connectionId") or "").strip()
    if not cid:
        return {"statusCode": 400, "body": "missing connectionId"}

    qs = event.get("queryStringParameters") or {}
    client_id = (qs.get("clientId") or "unknown").strip()
    account   = (qs.get("account") or "").strip()
    region    = (qs.get("region") or "").strip()
    source_ip = _extract_source_ip(event)

    now_sec = int(time.time())
    item = {
        "connectionId": cid,
        "createdAt": now_sec * 1000,
        "ttl": now_sec + TTL_HOURS * 3600,
        "clientId": client_id or "unknown",
    }
    if account:   item["account"]   = account
    if region:    item["region"]    = region
    if source_ip: item["sourceIp"]  = source_ip

    try:
        table.put_item(Item=item)
    except ClientError as e:
        print("put_item error:", e)
        return {"statusCode": 500, "body": "DB error"}

    return {"statusCode": 200, "body": "connected"}
