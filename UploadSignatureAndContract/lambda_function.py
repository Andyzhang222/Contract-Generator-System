import json
import boto3
import base64

def lambda_handler(event, context):
    
    signature_data = event['signature']
    contract_data = event['contract']

    s3 = boto3.client('s3')
    bucket_name = 'signaturedata'

    signature_key = 'signatureImage.png'
    s3.put_object(Bucket=bucket_name, Key=signature_key, Body=base64.b64decode(signature_data))

    contract_key = 'contractImage.png'
    s3.put_object(Bucket=bucket_name, Key=contract_key, Body=base64.b64decode(contract_data))

    return {
        'statusCode': 200,
        'body': json.dumps('Signature and contract uploaded successfully')
    }
