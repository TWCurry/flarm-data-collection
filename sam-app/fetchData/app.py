import os, boto3, requests

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
    
    # Fetch data
    try:
        xmlData = fetchData(loMax, loMin, laMax, laMin)
    except Exception as e:
        print(f"Could not fetch XML data - {e}")
        return{
            "statusCode": 500,
            "body": f"Error fetching data from OGN - {e}"
        }
    
    # Convert to sorta json document to write to DDB
    try:
        convertXml2Json(xmlData)
    except Exception as e:
        print(f"Could not convert XML to ddb json - {e}")
        return{
            "statusCode": 500,
            "body": f"Error converting data from XML - {e}"
        }

    return {
        "statusCode": 200,
        "body": "Function executed successfully"
    }

def fetchData(loMax, loMin, laMax, laMin):
    print("Fetching XML data...")
    params = {
        "a": 0,
        "b": laMax,
        "c": laMin,
        "d": loMax,
        "e": loMin,
        "z": 1
    }
    r = requests.get("https://live.glidernet.org/lxml.php", params=params)
    if r.status_code < 200 or r.status_code > 299:
        raise Exception(f"({r.status_code}) {r.text}")
    print("Successfully fetched XML data.")
    return r.text

def convertXml2Json(xmlData):
    for line in xmlData.splitlines():
        print(line)