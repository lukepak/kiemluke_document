import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


REGION = 'ap-northeast-1'
# SQS
QUEUE = "anhtt_scan_tasks.fifo"
MSG_GROUP_ID = "ScanTasks"
# Run task
CLUSTER = "tai-test-ci-tools"
DAST_CLUSTER = "ecs-cluster-dast"
LAUNCH_TYPE = "FARGATE"
PLATFORM_VER = "1.4.0"
SUBNET1 = "subnet-f89a008e"   # ci-subnet-pub-a
SUBNET2 = "subnet-bfa200e7"   # ci-subnet-pub-c
SECURITY_GROUP = "sg-03f97394e72442346"  # Access Internet
LAMBDA_UPDATE_TASK = "arn:aws:lambda:ap-northeast-1:012881927014:function:anhtt_update_task"


def lambda_handler(event, context):
    """
    1. ===Check ECS running tasks===
    2. ===Get message from SQS===
    3. ===Call ECS to run a task===
    4. Call API to update task status to RUNNING
    """

    if not event.get("type"):
        sast_cloc_process()
    elif event["type"] == "DAST":
        dast_process(event)
    else:
        logger.info(f"Unknow event: {event}")


def sast_cloc_process():
    logger.info("===== Start checking and scanning =====")
    try:
        tasks = get_running_task()
        logger.info(f"Got {len(tasks)} running tasks")
        if tasks:
            logger.info("Skip Scan")
            return

        messages = get_messages()
        logger.info(f"Got {len(messages)} message in queue")
        if not messages:
            logger.info("Skip Scan")
            return

        msg = messages[0]
        info = json.loads(msg.body)
        task_name = info['task_name']
        task_id = info['task_id']
        scan_type = info['type']
        logger.info(f"Received task: {task_name}")
        msg.delete()
        logger.info(f"Deleted Message")
        start_scan(task_name)

        payload = {'taskids': task_id, 'status': 'RUNNING', 'type': scan_type}
        update_status(payload)
    except Exception as e:
        logger.error(str(e))
        logger.error(f"task_id: {task_id}")
    finally:
        logger.info("===== Finish checking and scanning =====")


def get_running_task():
    client = boto3.client('ecs', region_name=REGION)

    logger.info(f"Getting ECS tasks on cluster {CLUSTER}")
    tasks = client.list_tasks(cluster=CLUSTER)
    return tasks.get('taskArns')


def get_messages():
    sqs = boto3.resource('sqs', region_name=REGION)
    queue = sqs.get_queue_by_name(QueueName=QUEUE)
    return queue.receive_messages()


def start_scan(task_name, cluster=CLUSTER):
    client = boto3.client('ecs', region_name=REGION)
    client.run_task(
        launchType=LAUNCH_TYPE,
        platformVersion=PLATFORM_VER,
        cluster=cluster,
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    SUBNET1,
                    SUBNET2
                ],
                'securityGroups': [
                    SECURITY_GROUP,
                ],
                'assignPublicIp': 'ENABLED'
            }
        },
        taskDefinition=task_name
    )
    return


def update_status(payload):
    client = boto3.client('lambda', region_name=REGION)
    logger.info(f"Calling lambda: {LAMBDA_UPDATE_TASK}")
    return client.invoke(
        FunctionName=LAMBDA_UPDATE_TASK,
        InvocationType="Event",
        Payload=json.dumps(payload)
    )


def dast_process(event):
    logger.info("===== Start scanning DAST =====")
    task_name = event['taskname']
    record_id = event['recordid']
    scan_type = event['type']
    try:
        start_scan(task_name, DAST_CLUSTER)
        payload = {'taskids': record_id, 'status': 'RUNNING', 'type': scan_type}
        update_status(payload)
    except Exception as e:
        logger.error(str(e))
        logger.error(f"DAST ID: {record_id}")
    finally:
        logger.info("===== Finish scanning DAST =====")

