import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
  logger.info('Incoming event: {}'.format(event))

  response = 'Received message body from API Gateway: {}'.format(event['Records'][0]['body'])
  logger.info(response)

  return {
    'statusCode': 200,
    'body': response
  }