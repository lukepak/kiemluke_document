import logging
import boto3
#Add comment for testing
logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'

EXECUTION_ROLE_ARN = "arn:aws:iam::012881927014:role/citool-ecs-task"
TASK_ROLE_ARN = "arn:aws:iam::012881927014:role/citool-ecs-task"
FILE_SYSTEM_ID = "fs-ae83948f"
AWS_LOGS_GROUP = "/ecs/7148_test-dast"


def lambda_handler(event, context):
    """
    Create a task definition
    """
    scan_type = event.get('type')
    if scan_type == "SAST":
        sast_def(event)
    elif scan_type == "CLOC":
        cloc_def(event)
    elif scan_type == "DAST":
        dast_def(event)
    elif scan_type == "SELENIUM":
        selenium_def(event)

# Automation test
def selenium_def(event):
    task_name = event.get('task_name')
    repo = event.get('repository')
    image = event.get('image')
    task_id = event.get('task_id')
    record_id = event.get('recordid')
    logger.info(f"Creating task definition for: {task_name}")
    try:
        register_selenium_task_definition(task_name, repo, image, task_id, record_id)
    except Exception as e:
        logger.error(str(e))
        logger.error(f"task_id: {task_id}")


def register_selenium_task_definition(task_name, repo, image, task_id, record_id):
    client = boto3.client('ecs', region_name=REGION)
    root_dir = '/' + record_id + '/' + repo
    cont_def = [
        {
            'name': repo.replace('.', 'dot'),
            'portMappings': [
                {
                    'containerPort': 22,
                    'hostPort': 22,
                    'protocol': 'tcp'
                },
            ],
            'workingDirectory': '/usr/src',
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-region': REGION,
                    'awslogs-group': AWS_LOGS_GROUP,
                    'awslogs-stream-prefix': 'ecs'
                },
            },
            'command': ["mvn","clean","verify"],
            'essential': True,
            'image': image,
            'mountPoints': [
                {
                    'sourceVolume': 'efs',
                    'containerPath': '/usr/src',
                    'readOnly': False
                },
            ]
        }
    ]

    volumes = [
        {
            'name': 'efs',
            'efsVolumeConfiguration': {
                'fileSystemId': FILE_SYSTEM_ID,
                'rootDirectory': root_dir,
                'transitEncryption': 'DISABLED',
                'authorizationConfig': {
                    'iam': 'DISABLED'
                }
            }
        }
    ]

    client.register_task_definition(
        containerDefinitions=cont_def,
        family=task_name,
        executionRoleArn=EXECUTION_ROLE_ARN,
        taskRoleArn=TASK_ROLE_ARN,
        networkMode='awsvpc',
        volumes=volumes,
        requiresCompatibilities=[
            'FARGATE',
        ],
        cpu='256',
        memory='2048',
        tags=[
            {
                'key': 'task_id',
                'value': task_id
            },
        ],
    )


def sast_def(event):
    task_name = event.get('task_name')
    repo = event.get('repository')
    image = event.get('image')
    task_id = event.get('task_id')
    record_id = event.get('recordid')
    exclude_path = event.get('excludepath')
    logger.info(f"Creating task definition for: {task_name}")
    try:
        register_task_definition(task_name, repo, image, task_id, record_id, exclude_path)
    except Exception as e:
        logger.error(str(e))
        logger.error(f"task_id: {task_id}")


def register_task_definition(task_name, repo, image, task_id, record_id, exclude_path):
    client = boto3.client('ecs', region_name=REGION)
    root_dir = '/' + record_id + '/' + repo
    cont_def = [
        {
            'name': repo.replace('.', 'dot'),
            'portMappings': [
                {
                    'containerPort': 22,
                    'hostPort': 22,
                    'protocol': 'tcp'
                },
            ],
            'environment': [
                {
                    'name': 'CI_PROJECT_DIR',
                    'value': '/tmp/app'
                },
                {
                    'name': 'SAST_EXCLUDED_PATHS',
                    'value': exclude_path
                },
                {
                    'name': 'SAST_BANDIT_EXCLUDED_PATHS',
                    'value': exclude_path
                },
            ],
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-region': REGION,
                    'awslogs-group': AWS_LOGS_GROUP,
                    'awslogs-stream-prefix': 'ecs'
                },
            },
            'essential': True,
            'image': image,
            'mountPoints': [
                {
                    'sourceVolume': 'efs',
                    'containerPath': '/tmp/app',
                    'readOnly': False
                },
            ]
        }
    ]

    volumes = [
        {
            'name': 'efs',
            'efsVolumeConfiguration': {
                'fileSystemId': FILE_SYSTEM_ID,
                'rootDirectory': root_dir,
                'transitEncryption': 'DISABLED',
                'authorizationConfig': {
                    'iam': 'DISABLED'
                }
            }
        }
    ]

    client.register_task_definition(
        containerDefinitions=cont_def,
        family=task_name,
        executionRoleArn=EXECUTION_ROLE_ARN,
        taskRoleArn=TASK_ROLE_ARN,
        networkMode='awsvpc',
        volumes=volumes,
        requiresCompatibilities=[
            'FARGATE',
        ],
        cpu='256',
        memory='2048',
        tags=[
            {
                'key': 'task_id',
                'value': task_id
            },
        ],
    )


def cloc_def(event):
    task_name = event.get('task_name')
    repo = event.get('repository')
    image = event.get('image')
    record_id = event.get('recordid')
    include_lang = event.get('includelang')
    exclude_dir = event.get('excludedir')
    commit_id1 = event.get('commitid1')
    commit_id2 = event.get('commitid2')
    compared_branch1 = event.get('comparedbranch1')
    compared_branch2 = event.get('comparedbranch2')

    logger.info(f"Creating task definition for: {task_name}")
    try:
        register_cloc_task_definition(task_name, repo, image, record_id, include_lang, exclude_dir, commit_id1,
                                      commit_id2, compared_branch1, compared_branch2)
    except Exception as e:
        logger.error(str(e))
        logger.error(f"task_id: {record_id}")


def register_cloc_task_definition(task_name, repo, image, record_id, include_lang, exclude_dir,
                                  commit_id1=None, commit_id2=None, compared_branch1=None, compared_branch2=None):
    client = boto3.client('ecs', region_name=REGION)
    root_dir = '/' + record_id + '/' + repo

    if compared_branch1 and compared_branch2 != "None":
        base_command = ["--git-diff-rel", compared_branch1, compared_branch2, "--timeout", "0"]
        if include_lang != "*":
            base_command.append(f"--include-lang={include_lang.replace(' ', '')}")
        if exclude_dir != "*":
            base_command.append(f"--exclude-dir={exclude_dir.replace(' ', '')}")
        command1 = base_command[::]
        command1.extend(["--json", "--out=cloc_comparison_summary.json"])
    elif commit_id1 and commit_id2 != "None":
        base_command = ["--git-diff-rel", commit_id1, commit_id2, "--timeout", "0"]
        if include_lang != "*":
            base_command.append(f"--include-lang={include_lang.replace(' ', '')}")
        if exclude_dir != "*":
            base_command.append(f"--exclude-dir={exclude_dir.replace(' ', '')}")
        command1 = base_command[::]
        command1.extend(["--json", "--out=cloc_comparison_summary.json"])
    else:
        base_command = [".", "--timeout", "0"]
        if include_lang != "*":
            base_command.append(f"--include-lang={include_lang.replace(' ', '')}")

        if exclude_dir != "*":
            base_command.append(f"--exclude-dir={exclude_dir.replace(' ', '')}")

        command1 = base_command[::]
        command1.extend(["--json", "--out=cloc_summary.json"])

    command2 = base_command[::]
    command2.extend(["--by-file", "--csv", "--out=cloc_detail.csv"])

    base_con_def = {
        'workingDirectory': '/tmp/app',
        'logConfiguration': {
            'logDriver': 'awslogs',
            'options': {
                'awslogs-region': REGION,
                'awslogs-group': AWS_LOGS_GROUP,
                'awslogs-stream-prefix': 'ecs'
            },
        },
        'essential': True,
        'image': image,
        'mountPoints': [
            {
                'sourceVolume': 'efs',
                'containerPath': '/tmp/app',
                'readOnly': False
            },
        ],
    }

    cont_def = [
        {**base_con_def, 'name': repo + "_byLang", "command": command1, 'portMappings': [{'containerPort': 23}]},
        {**base_con_def, 'name': repo + "_byFile", "command": command2, 'portMappings': [{'containerPort': 24}]},
    ]

    volumes = [
        {
            'name': 'efs',
            'efsVolumeConfiguration': {
                'fileSystemId': FILE_SYSTEM_ID,
                'rootDirectory': root_dir,
                'transitEncryption': 'DISABLED',
                'authorizationConfig': {
                    'iam': 'DISABLED'
                }
            }
        }
    ]

    client.register_task_definition(
        containerDefinitions=cont_def,
        family=task_name,
        executionRoleArn=EXECUTION_ROLE_ARN,
        taskRoleArn=TASK_ROLE_ARN,
        networkMode='awsvpc',
        volumes=volumes,
        requiresCompatibilities=[
            'FARGATE',
        ],
        cpu='512',
        memory='2048',
        tags=[
            {
                'key': 'task_id',
                'value': record_id
            },
        ],
    )


def dast_def(event):
    task_name = event.get('taskname')
    image = event.get('image')
    record_id = event.get('recordid')
    target_url = event.get('targeturl')
    full_scan = event.get('fullscan')
    dast_path = event.get("dastpath")
    file_name = event.get("filename")
    header_token = event.get("header_token")

    logger.info(f"Creating task definition for: {task_name}")
    try:
        if not file_name:
            if not header_token:
                register_dast_task_definition(task_name, image, record_id, full_scan, dast_path, target_url=target_url)
            else:
                register_dast_task_definition(task_name, image, record_id, full_scan, dast_path, target_url=target_url,
                                              header_token=header_token)
        else:
            if not header_token:
                register_dast_task_definition(task_name, image, record_id, full_scan, dast_path, file_name=file_name)
            else:
                register_dast_task_definition(task_name, image, record_id, full_scan, dast_path, file_name=file_name,
                                              header_token=header_token)
    except Exception as e:
        logger.error(str(e))
        logger.error(f"task_id: {record_id}")


def register_dast_task_definition(task_name, image, record_id, full_scan, dast_path, target_url=None,
                                  file_name=None, header_token=None):
    client = boto3.client('ecs', region_name=REGION)
    if target_url is not None:
        if header_token is not None:
            command = ["/analyze", "-t", target_url, "-r", "report.html", "--full-scan", str(full_scan).lower(),
                       "--request-headers", header_token]
        else:
            command = ["/analyze", "-t", target_url, "-r", "report.html", "--full-scan", str(full_scan).lower()]
    elif file_name is not None:
        if header_token is not None:
            command = ["/analyze", "--api-specification", file_name, "-r", "report.html", "--full-scan",
                       str(full_scan).lower(), "--request-headers", header_token]
        else:
            command = ["/analyze", "--api-specification", file_name, "-r", "report.html", "--full-scan",
                       str(full_scan).lower()]
    if dast_path:
        command.extend(["--paths-to-scan", dast_path])
    root_dir = '/' + record_id + '/wrk'
    cont_def = [
        {
            'name': record_id,
            'workingDirectory': '/output',
            'portMappings': [
                {
                    'containerPort': 22,
                },
            ],
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-region': REGION,
                    'awslogs-group': AWS_LOGS_GROUP,
                    'awslogs-stream-prefix': 'ecs'
                },
            },
            'essential': True,
            'command': command,
            'image': image,
            'mountPoints': [
                {
                    'sourceVolume': 'efs',
                    'containerPath': '/output',
                },
                {
                    'sourceVolume': 'efs',
                    'containerPath': '/zap/wrk',
                },
            ]
        }
    ]

    volumes = [
        {
            'name': 'efs',
            'efsVolumeConfiguration': {
                'fileSystemId': FILE_SYSTEM_ID,
                'rootDirectory': root_dir,
                'transitEncryption': 'DISABLED',
                'authorizationConfig': {
                    'iam': 'DISABLED'
                }
            }
        }
    ]

    if str(full_scan).lower() == "true":
        client.register_task_definition(
            containerDefinitions=cont_def,
            family=task_name,
            executionRoleArn=EXECUTION_ROLE_ARN,
            taskRoleArn=TASK_ROLE_ARN,
            networkMode='awsvpc',
            volumes=volumes,
            requiresCompatibilities=[
                'FARGATE',
            ],
            cpu='1024',
            memory='4096',
            tags=[
                {
                    'key': 'task_id',
                    'value': record_id
                },
            ],
        )
    else:
        client.register_task_definition(
            containerDefinitions=cont_def,
            family=task_name,
            executionRoleArn=EXECUTION_ROLE_ARN,
            taskRoleArn=TASK_ROLE_ARN,
            networkMode='awsvpc',
            volumes=volumes,
            requiresCompatibilities=[
                'FARGATE',
            ],
            cpu='512',
            memory='2048',
            tags=[
                {
                    'key': 'task_id',
                    'value': record_id
                },
            ],
        )

