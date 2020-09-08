import os, boto3, sys, json
from boto3 import resource
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    #Query Parameters
    try:
        aircraftId = event["queryStringParameters"]["trigraph"]
    except Exception as e:
        print(f"Invalid parameters - {e}")
        return {
            "statusCode": 400,
            "body": f"Invalid parameters - {e}"
        }
    # Environment variables
    try:
        tableName = os.environ["tableName"]
    except Exception as e:
        print(f"Invalid environment variables - {e}")
        return {
            "statusCode": 500,
            "body": f"Invalid environment variables - {e}"
        }
    try:
        flightData = fetchData(tableName, aircraftId)
    except Exception as e:
        print(f"Could not read data from DynamoDB - {e}")
        return {
            "statusCode": 500,
            "body": f"Could not read data from DynamoDB - {e}"
        }
    
    return{
        "statusCode": 200,
        "isBase64Encoded": "false",
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": {
            "Items": json.dumps(flightData)
        }
    }

def fetchData(tableName, aircraftId):
    client = boto3.client("dynamodb")
    items = []
    response = client.query(
        ExpressionAttributeValues={
            ':v1': {
                'S': aircraftId,
            },
        },
        KeyConditionExpression='trigraph = :v1',
        TableName=tableName,
        IndexName="trigraph-index",
        Select="ALL_ATTRIBUTES",

    )
    for item in response["Items"]:
        newItem = {}
        for key, value in item.items():
            if key != "ttl":
                newItem[key] = value["S"]
        items.append(newItem)
    return items