import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

TABLE_NAME = 'FileMetadata'
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:YOUR_ACCOUNT_ID:FileUploadAlert'

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_name = record['s3']['object']['key']
        file_size = record['s3']['object'].get('size', 0)
        upload_time = datetime.now().isoformat()

        print("New file detected:", file_name, "in bucket", bucket_name)

        table.put_item(
            Item={
                'FileName': file_name,
                'UploadTime': upload_time,
                'Bucket': bucket_name,
                'SizeBytes': file_size
            }
        )

        print("Metadata saved to DynamoDB")

        msg = "File " + file_name + " (" + str(file_size) + " bytes) uploaded to " + bucket_name + " at " + upload_time

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='File Upload Successful',
            Message=msg
        )

        print("Email notification sent")

    return {
        'statusCode': 200,
        'body': 'Success'
    }
