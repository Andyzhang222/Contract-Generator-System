import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    bucket_name = 'signaturedata'
    file_key = 'contract_signature.pdf'
    
    
    s3_client = boto3.client('s3')
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=3600
        )
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        raise
    
    message = f"Please find the document  attached. You can access it using the following link: {presigned_url}"
    
    sns = boto3.client('sns')
    
    subject = 'Document with Image'
    
    topic_arn = 'arn:aws:sns:us-east-1:471112996976:andy'
    
    response = sns.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message
    )

    return {
        'statusCode': 200,
        'body': 'Email sent successfully!'
    }
