import logging
import json
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'
IMAGE_MAPPING = {
    "php": "registry.gitlab.com/gitlab-org/security-products/analyzers/phpcs-security-audit:2",
    "java": "registry.gitlab.com/gitlab-org/security-products/analyzers/spotbugs:2",
    ".net": "registry.gitlab.com/gitlab-org/security-products/analyzers/security-code-scan:2",
    "python": "registry.gitlab.com/gitlab-org/security-products/analyzers/semgrep",
    "eslint": "registry.gitlab.com/gitlab-org/security-products/analyzers/eslint:2",
    "secret": "registry.gitlab.com/gitlab-org/security-products/analyzers/secrets:3",
}

QUEUE = 'anhtt_scan_tasks.fifo'
MSG_GROUP_ID = "ScanTasks"
CREATE_TASK_LAMBDA = "arn:aws:lambda:ap-northeast-1:012881927014:function:anhtt_create_task_def"
SCAN_LAMBDA = "arn:aws:lambda:ap-northeast-1:012881927014:function:anhtt_check_and_scan"
TASK_NAME_FORM = "{repo}_{language}_{type}"


def lambda_handler(event, context):
    """
    1. Call lambda to create task definition
    2. Push task name to message queue
    3. Call lambda to check and run task
    """
    logging.info("===== Start scheduling task =====")
    repository = event.get('repository')
    language = event.get('language')
    scan_type = event.get('type')
    recordid = event.get('recordid')
    if not repository or not language or not scan_type:
        logger.error(f"Task name does not specified: {event}")
        return

    image = IMAGE_MAPPING.get(language)
    if not image:
        logger.error(f"Not supported program language: {language}")
        return

    try:
        task_name = TASK_NAME_FORM.format(repo=repository, language=language, type=scan_type)
        payload = {
            "task_name": task_name,
            "repository": repository,
            "image": image,
            "recordid": recordid,
        }
        response = call_lambda(CREATE_TASK_LAMBDA, payload, "RequestResponse")
        if response["StatusCode"] != 200:
            logger.error(f"Create task failed: {response}")

        info = {
            "task_name": task_name,
            "recordid": recordid,
        }
        response = push_sqs_message(info)
        if response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
            logger.error(f"Unexpected error: {response}")
            return
        logger.info("Sent message successfully")

        call_lambda(SCAN_LAMBDA, {}, "Event")  # asynchronously

    except Exception as e:
        logger.error(str(e))

    finally:
        logging.info("===== Finish scheduling task =====")


def push_sqs_message(info):
    logger.info("Sending message")
    sqs = boto3.resource('sqs', region_name=REGION)
    queue = sqs.get_queue_by_name(QueueName=QUEUE)
    response = queue.send_message(
        MessageBody=json.dumps(info),
        MessageGroupId=MSG_GROUP_ID
    )
    return response


def call_lambda(function, payload, invoke_type):
    client = boto3.client('lambda', region_name=REGION)
    logger.info(f"Calling lambda: {function}")
    return client.invoke(
        FunctionName=function,
        InvocationType=invoke_type,
        Payload=json.dumps(payload)
    )

