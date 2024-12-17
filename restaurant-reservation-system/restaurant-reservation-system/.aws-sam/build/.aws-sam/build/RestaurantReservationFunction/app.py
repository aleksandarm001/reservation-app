import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Inicijalizacija DynamoDB i SNS klijenata
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
sns_topic_arn = os.environ['SNS_TOPIC_ARN']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):


    try:
        logger.info(f"Using DynamoDB Table: {os.environ['DYNAMODB_TABLE']}")
        logger.info(f"Using SNS Topic ARN: {os.environ['SNS_TOPIC_ARN']}")
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    except KeyError as e:
        logger.error(f"Missing environment variable: {str(e)}")
        raise

    # Obrada GET zahteva na /status putanji
    if event['httpMethod'] == 'GET' and event['path'] == '/status':
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Server radi!'})
        }
    
    if event['httpMethod'] == 'POST' and event['path'] == '/create':

        try:
            # Parsiranje JSON tela zahteva
            body = json.loads(event['body'])
            item = {
                'reservation_id': body['reservation_id'],  # Pretpostavljamo da šalješ 'id' kao jedinstveni ključ
                'name': body['name'],
                'description': body['description']
            }

            # Unos objekta u DynamoDB
            response = table.put_item(Item=item)

            # Logovanje uspeha
            logger.info(f"PutItem succeeded: {response}")
            
            # Vraćanje odgovora sa status kodom 201 (kreiran)
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Objekat je uspešno kreiran!'})
            }
        
        except KeyError as e:
            logger.error(f"Missing key in request body: {str(e)}")
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f"Missing key in request body: {str(e)}"})
            }
        except ClientError as e:
            logger.error(f"Error inserting item: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f"Error inserting item: {str(e)}"})
            }