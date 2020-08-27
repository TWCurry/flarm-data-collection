import os, boto3, requests, uuid

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
            "statusCode": 400,
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
    client = boto3.client('dynamodb')
    for obj in jsonData:
        ddbWriteOb = {"id": {"S": uuid.uuid4().hex}} #Assign random hex as the id of the record in ddb
        for key, value in obj.items():
            ddbWriteOb[key] = {"S": str(value)}
        r = client.put_item(
            TableName=tableName,
            Item=ddbWriteOb
        )
    print(f"Completed write to db. Written {len(jsonData)} items.")