import gzip
import json
import boto3
import base64
import logging
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'
DYNAMO_DB = "user-api"
# Task API
API = "http://citools.citeam.work:6965/api/scan/subtask/"


def lambda_handler(event, context):
    """
    uncompressed event
    """
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    
    log_events = payload['logEvents']
    logger.info(log_events)
    
    for log_event in log_events:
        logger.info(log_event['extractedFields']['task_id'])
        update_status(
            log_event['extractedFields']['task_id'],
            "ERROR"
        )
    
    return 0

def update_status(task_id, status):
    api = API + task_id
    token = get_token()
    headers = {"Authorization": f"JWT {token}"}
    data = {"status": status}

    http = urllib3.PoolManager()
    response = http.request('PUT', api, fields=data, headers=headers)
    if response.status != 200:
        logger.error(f"Error when update task status: {response.data}")
    else:
        logger.info("Update task successfully")


def get_token():
    logger.info("Getting token from dynamodb")
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table('user-api')
    response = table.get_item(Key={'id': 'task_api_token'})

    return response['Item']['token']

