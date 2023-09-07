import json
import gzip
import base64
import boto3
from datetime import datetime
import io

def upload_gz(s3client, bucket, key, obj, encoding='utf-8'):
    ''' upload python dict into s3 bucket with gzip archive '''
    inmem = io.BytesIO()
    with gzip.GzipFile(fileobj=inmem, mode='wb') as fh:
        with io.TextIOWrapper(fh, encoding=encoding) as wrapper:
            wrapper.write(obj)
    inmem.seek(0)
    s3client.put_object(Bucket=bucket, Body=inmem, Key=key)

def lambda_handler(event, context):
    kongCP_Auth = 'CP_r8q2DLoM2RY4RG2luPvF'
    kongDP_Auth = 'DP_atDUfLaFZlEeJUbt4P58'
    bucketS3    = 'kong-log-processing-axa'
    reqBody = ''
    contentEncoding = ''
    errMessage = {}
    authorization = ''
    error = False
    keyS3 = ''

    # Get Authorization Header
    try:
        headers = event["headers"]
        print("headers: " + json.dumps(headers))
        authorizationHeader = headers["authorization"]
        print("authorization Bearer: " + authorizationHeader)
        if len(authorizationHeader):
            authSplit = authorizationHeader.split("Bearer ", 1)
            authorization = authSplit[1]
        if not len(authorization):
            error = True    
    except:
        error = True
        print("No Authorization header")

    # If there is an Auth header
    if not error:
        # If the Auth is neither KongCP nor Kong KongDP
        if authorization != kongCP_Auth and authorization != kongDP_Auth:
            error = True
            print("Authorization code is invalid")

    # If we don't find a suitable Authorization
    if error:
        errMessage = {"Error": "Unauthorized"}
        return {
            'statusCode': 401,
            'body': errMessage
        }         

    # Get 'Content-Encoding' on the Request
    try:
        contentEncoding = headers["content-encoding"]
    except:
        print("No Content-Encoding header")
    
    # If there is an a gzip 'Content-Encoding' we decompress it
    if contentEncoding == "gzip":
        print("Content-Encoding is: " + contentEncoding )
        if "body" in event:
            try:
                bytesBody = base64.b64decode(event["body"])
                reqBody = gzip.decompress(bytesBody).decode('utf-8')
            except Exception as ex:
                reqBody = ''
                print("Unable to decompress the 'body', exception={}".format(ex))
    # If the Content-Eoncoding is not supported by this program
    elif len(contentEncoding):
        error = True
        print("Content-Encoding '" + contentEncoding + "' is not supported")

    else:
        if "body" in event:
            reqBody = event["body"]
    
    if len(reqBody):
        print("Request Body: '" + reqBody + "'")
        # Write in S3 bucket
        try:
            s3client = boto3.client('s3')
            now = datetime.now() # current date and time
            fileName=now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            
            if authorization == kongCP_Auth:
                dirName = 'Kong_CP'
            elif authorization == kongDP_Auth:
                dirName = 'Kong_DP'
            else:
                dirName = 'Unknown'
            
            keyS3 = dirName + '/' + fileName + '.json.gz'
            print("key S3: " + keyS3)

            # Write in S3
            # s3client.put_object(
            #    Body=reqBody, 
            #    ContentType='application/json',
            #    Bucket=bucketS3,
            #    Key=keyS3
            #)
            upload_gz(s3client, bucketS3, keyS3, reqBody, 'utf-8')
            
        except Exception as ex:
            print("Unable to write the 'body' in S3, exception={}".format(ex))
            errMessage = {"Error": "Failure for writing in S3 bucket"}
            return {
                'statusCode': 500,
                'body': errMessage
            }
    else:
        print("Failure for retrieving/handling the 'body' content")
        errMessage = {"Error": "Failure for retrieving/handling the 'body' content"}
        return {
            'statusCode': 500,
            'body': errMessage
        }
    
    return {
        'statusCode': 200,
        'body': 'Successfully pushed logs'
    }
