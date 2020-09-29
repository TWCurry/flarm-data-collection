import os, boto3, requests, uuid, time

def lambda_handler(event, context):
    # Environment variables
    try:
        loMax = os.environ["loMax"]
        loMin = os.environ["loMin"]
        laMax = os.environ["laMax"]
        laMin = os.environ["laMin"]
        tableName = os.environ["tableName"]
        logGroupName = os.environ["logGroupName"]
    except Exception as e:
        return {
            "statusCode": 400,
            "body": f"Invalid environment variables - {e}"
        }
    # Log execution time
    logExecution(logGroupName)

    # Fetch data
    try:
        xmlData = fetchData(loMax, loMin, laMax, laMin)
    except Exception as e:
        print(f"Could not fetch XML data - {e}")
        return{
            "statusCode": 500,
            "body": f"Error fetching data from OGN - {e}"
        }
    
    # Convert to json document
    try:
        jsonObjects = convertXml2Json(xmlData)
    except Exception as e:
        print(f"Could not convert XML to json - {e}")
        return{
            "statusCode": 500,
            "body": f"Error converting data from XML - {e}"
        }
    
    # Write to dynamodb
    try:
        writeToDb(jsonObjects, tableName)
    except Exception as e:
        print(f"Could not write to db - {e}")
        return{
            "statusCode": 500,
            "body": f"Error writing to db - {e}"
        }

    return {
        "statusCode": 200,
        "body": "Function executed successfully"
    }

def logExecution(logGroupName):
    client = boto3.client('logs')
    logStreamData = client.describe_log_streams(
        logGroupName=logGroupName
    )
    uploadSequenceToken = logStreamData["logStreams"][0]["uploadSequenceToken"]
    timestamp = int(round(time.time() * 1000))
    response = client.put_log_events(
        logGroupName=logGroupName,
        logStreamName="Executions",
        logEvents=[
            {
                "timestamp": timestamp,
                "message": f"Function executed at {str(time.strftime('%Y-%m-%d %H:%M:%S'))}UTC"
            },
        ],
        sequenceToken=uploadSequenceToken
    )

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
    print("Converting XML to JSON...")
    outputJson = []
    markerSection = False
    for line in xmlData.splitlines():
        if line == "</markers>": #If we've reached the end of the data, we don't need to care about the rest of the loop
            break

        if markerSection == True: # Only care about the lines in the marker section 
            lineData = line[6:-3].split(",")
            outputJson.append({
                "latitude": lineData[0],
                "longitude": lineData[1],
                "trigraph": lineData[2],
                "acId": lineData[3],
                "altitude": lineData[4],
                "time": lineData[5],
                "track": lineData[7],
                "gSpeed": lineData[8],
                "vSpeed": lineData[9],
                "receiver": lineData[11],
                "hex": lineData[13]
            })

        if line == "<markers>":
            markerSection = True
    print("Successfully converted XML to JSON.")
    return outputJson

def writeToDb(jsonData, tableName):
    print("Beginning write to db...")
    timestamp = int(time.time())
    dbObjs = [] #Array of ddb formatted data

    #Create items to write
    for obj in jsonData:
        ddbWriteOb = {"id": uuid.uuid4().hex} #Assign random hex as the id of the record in ddb
        ddbWriteOb["ttl"] = str(timestamp+172800) #Add TTL of 2 days
        for key, value in obj.items():
            if key == "trigraph" and value == "": value = "UNKNOWN"
            if key == "acId" and value == "": value = "UNKNOWN"
            ddbWriteOb[key] = str(value)
        dbObjs.append(ddbWriteOb)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)

    #Batch write to db for improved performance
    with table.batch_writer() as writer:
        for item in dbObjs:
            print(item)
            writer.put_item(Item=item)

    print(f"Completed write to db. Written {len(jsonData)} items.")