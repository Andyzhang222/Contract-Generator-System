import json
import boto3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import tempfile

def lambda_handler(event, context):
    # Initialize AWS clients
    s3 = boto3.client('s3')
    textract = boto3.client('textract')
    bucket_name = 'signaturedata'

    contract_image_path = 'contractImage.png'
    
    # Fetch the contract image from S3
    contract_image_object = s3.get_object(Bucket=bucket_name, Key=contract_image_path)
    contract_image_content = contract_image_object['Body'].read()

    textract_response = textract.detect_document_text(
        Document={'Bytes': contract_image_content}
    )

    text_blocks = [item['Text'] for item in textract_response['Blocks'] if item['BlockType'] == 'LINE']

    # Create a temporary file for the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        output_path = tmp_pdf.name

        # Generate the PDF with Textract data
        c = canvas.Canvas(output_path, pagesize=letter)
        c.setFont("Helvetica", 10)
        text_object = c.beginText(40, 750)  # Starting position

        for line in text_blocks:
            text_object.textLine(line)
        
        c.drawText(text_object)
        
        # Add the label for the signature
        signature_label_x = 50  
        signature_label_y = 120  
        c.drawString(signature_label_x, signature_label_y, "Handwriting Signature:")

        # Add the signature image to the PDF
        signature_image_path = 'signatureImage.png'
        signature_image_object = s3.get_object(Bucket=bucket_name, Key=signature_image_path)
        signature_image_content = signature_image_object['Body'].read()
        
        # Create a temporary file for the signature image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_image:
            tmp_image.write(signature_image_content)
            tmp_image_path = tmp_image.name
            
            img = Image.open(tmp_image_path)
            width, height = img.size
            aspect_ratio = height / width
            c.drawImage(tmp_image_path, 100, 100, width=400, height=400 * aspect_ratio, mask='auto')
        
        c.save()

    # Upload the PDF to S3
    with open(output_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    s3.put_object(Bucket=bucket_name, Key='contract_signature.pdf', Body=pdf_content)

    return {
        'statusCode': 200,
        'body': json.dumps('PDF with extracted text and signature uploaded successfully!')
    }
