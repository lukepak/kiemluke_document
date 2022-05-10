import os
import logging
import boto3
import urllib3
import json
from datetime import datetime, timedelta
# Added comment for testing codebuild

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'
DYNAMO_DB = "user-api"
TTL = 23    # time in hours, when the dynamodb item will be removed
SG_ID = 'sg-028cb74573c238ddd'

# Auth API
API = "https://microscan.teamci.work/api/auth/login/"


def lambda_handler(event, context):
    logger.info(f'Stream record: {event["Records"]}')
    renew_token = False
    for r in event["Records"]:
        if r["eventName"] != 'REMOVE':
            continue
        if r["dynamodb"]["Keys"] != {'id': {'S': 'task_api_token'}}:
            continue
        renew_token = True

    if not renew_token:
        logger.info("====== Skip renewing token ======")
        return

    logger.info("====== Start renewing token ======")
    logger.info('Open ALB before get token')
    update_security_group_rule(True)
    
    token = get_token(
        os.environ['SYSTEM_USER'],
        os.environ['SYSTEM_PASS']
    )
    logger.info('Close ALB after get token')
    update_security_group_rule(False)
    
    insert_token(token)
    logger.info("====== Token has been renewed ======")


def get_token(user, passwd):
    logger.info("Calling authen api to get token")
    http = urllib3.PoolManager()
    body = {
        "email": user,
        "password": passwd
    }
    r = http.request('POST', API, fields=body)
    if r.status != 200:
        logger.error(f"Cannot get token: {r.data}")
        return ""
    data = json.loads(r.data.decode('utf-8'))
    return data["token"]


def insert_token(token):
    logger.info("Inserting token to dynamodb")
    client = boto3.client('dynamodb', region_name=REGION)

    now = datetime.now()
    ttl = now + timedelta(hours=TTL)

    client.put_item(
        TableName=DYNAMO_DB,
        Item={
            'id': {
                'S': 'task_api_token',
            },
            'token': {
                'S': token,
            },
            'renew_token': {
                'N': str(int(ttl.timestamp()))
            }
        }
    )
    
def update_security_group_rule(is_open):
    client = boto3.client('ec2', region_name=REGION)
    
    try:
        if is_open:
            response = client.authorize_security_group_ingress(
                GroupId=SG_ID,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0'
                            }
                        ]
                    }
                ]
            )
        else:
            response = client.revoke_security_group_ingress(
                GroupId=SG_ID,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0'
                            }
                        ]
                    },
                ]
            )
    except Exception as e:
        logger.error(e)

