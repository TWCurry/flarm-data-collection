import os, boto3
def lambda_handler(event, context):
    # Environment variables
    try:
        loMax = os.environ["loMax"]
        loMin = os.environ["loMin"]
        laMax = os.environ["laMax"]
        laMin = os.environ["laMin"]
        tableName = os.environ["tableName"]
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Invalid environment variables - {e}"
        }
    # https://live.glidernet.org/lxml.php?a=0&b=59.355596110016315&c=49.61070993807422&d=3.6474609375000004&e=-13.710937500000002&z=1
    return {
        "statusCode": 200,
        "body": "Function executed successfully"
    }