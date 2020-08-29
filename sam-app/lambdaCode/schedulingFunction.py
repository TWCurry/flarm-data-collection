import os, boto3

def lambda_handler(event, context):
    # Environment variables
    try:
        functionName = os.environ["functionToTrigger"]
        queueUrl = os.environ["queueUrl"]
    except Exception as e:
        return {
            "statusCode": 400,
            "body": f"Invalid environment variables - {e}"
        }

    # Schedule lambdas
    try:
        scheduleLambdas(queueUrl, functionName)
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

def scheduleLambdas(queueUrl, functionName):
    client = boto3.client('sqs')
    messages = []
    for i in range(10):
        messages.append({
            "Id": str(i),
            "MessageBody": f"Trigger for fetch lambda, delayed by {i*5} seconds",
            "DelaySeconds": int(i)*5
        })
    messages2 = [] #Second set since send_message_batch can only handle 10 messages
    for i in range(2):
        messages2.append({
            "Id": str(i),
            "MessageBody": f"Trigger for fetch lambda, delayed by {(i+10)*5} seconds",
            "DelaySeconds": (int(i)+10)*5
        })
    r = client.send_message_batch(
        QueueUrl=queueUrl,
        Entries=messages
    )
    r = client.send_message_batch(
        QueueUrl=queueUrl,
        Entries=messages2
    )