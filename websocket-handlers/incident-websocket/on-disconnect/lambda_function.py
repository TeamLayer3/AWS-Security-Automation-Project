# file: history_disconnect.py
import os, boto3
from botocore.exceptions import ClientError

CONNECTIONS_TABLE = os.environ["CONNECTIONS_TABLE"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(CONNECTIONS_TABLE)

def lambda_handler(event, context):
    cid = event["requestContext"]["connectionId"]
    try:
        table.delete_item(Key={"connectionId": cid})
        print("deleted:", cid)
    except ClientError as e:
        print("delete_item error:", e)
    return {"statusCode": 200, "body": "disconnected"}
