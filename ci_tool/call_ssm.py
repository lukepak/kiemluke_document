import boto3
import logging
import json
from urllib.parse import quote_plus
# Added comment for testing
logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'
SSM_MAPPING = {
    "SAST": 'Sast-CloneRepoDocument',
    "CLOC": 'Cloc-CloneRepoDocument',
    "SELENIUM": 'Selenium-CloneRepoDocument',
    "DEPENDENCY": 'Owasp-CloneRepoDocument'
}

# SQS
QUEUE = "anhtt_clone_tasks.fifo"
MSG_GROUP_ID = "CloneTasks"


def lambda_handler(event, context):
    """
    1. ===Get message from sqs===
    2. ===Update password to ssm param===
    3. ===Update user to ssm param===
    4. ===Call ssm to clone repo===
    """
    logger.info("=========== Start checking and clone source ===========")
    logger.info("Getting message from sqs")
    messages = get_messages()
    logger.info(f"Got {len(messages)} message in queue")
    if not messages:
        logger.info("Skip Clone")
        update_password("xxxxxxxxxx")
        update_user("xxxxxxxxxx")
        return

    msg = messages[0]
    info = json.loads(msg.body)
    logger.info(f"Received task: {info['giturl']}")
    msg.delete()

    update_password(info["gitpassword"])
    update_user(info["gituser"])
    info.pop("gitpassword")
    info.pop("gituser")
    ssm_name = SSM_MAPPING[info["type"]]
    info = {k: [v] for k, v in info.items()}

    call_ssm(ssm_name, info)
    logger.info("=========== Finish checking and clone source ===========")


def get_messages():
    sqs = boto3.resource('sqs', region_name=REGION)
    queue = sqs.get_queue_by_name(QueueName=QUEUE)
    return queue.receive_messages()


def update_password(passwd):
    logger.info("Updating password to ssm parameter")
    client = boto3.client('ssm', region_name=REGION)

    response = client.put_parameter(
        Name='/citools/fargate/gitclone/password',
        Value=quote_plus(passwd),
        Type='SecureString',
        Overwrite=True,
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        logger.info("Update password successfully")
    else:
        logger.error(f"Error when updating password: {response}")


def update_user(user):
    logger.info("Updating user to ssm parameter")
    client = boto3.client('ssm', region_name=REGION)

    response = client.put_parameter(
        Name='/citools/fargate/gitclone/gituser',
        Value=quote_plus(user),
        Type='SecureString',
        Overwrite=True,
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        logger.info("Update user successfully")
    else:
        logger.error(f"Error when updating user: {response}")


def call_ssm(name, params):
    logger.info("Calling ssm to clone source code")
    logger.info(params)
    client = boto3.client('ssm', region_name=REGION)

    try:
        response = client.start_automation_execution(
            DocumentName=name,
            Parameters=params,
        )
        logger.info(response)
    except Exception as e:
        logger.error(str(e))
    else:
        logger.info("Call ssm successfully")

