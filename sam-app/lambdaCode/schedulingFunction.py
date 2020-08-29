import os, boto3

def lambda_handler(event, context):
    # Environment variables
    try:
        functionName = os.environ["functionToTrigger"]
        queueUrl = os.environ["queueUrl"]
        print(queueUrl)
    except Exception as e:
        return {
            "statusCode": 400,
            "body": f"Invalid environment variables - {e}"
        }

    # Schedule lambdas
    try:
        scheduleLambdas(functionName)
    except Exception as e:
        print(f"Could not post to SQS - {e}")
        return {
            "statusCode": 500,
            "body": f"Could not post to SQS - {e}"
        }
    return {
        "statusCode": 200,
        "body": "Function executed successfully"
    }

# def scheduleLambdas(functionName):
