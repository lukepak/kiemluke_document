import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # TODO implement
    user_id = event['pathParameters']['userId']
    logger.info(f"========== Unsub: {user_id}")
    return {
        'statusCode': 200,
        'body': """
            <h1>Thank You</h1>
            <p>
                You have been successfully removed from this subscriber list and won't receive any further email from us.
            </p>
        """,
        "headers": {
            'Content-Type': 'text/html',
        }
    }

