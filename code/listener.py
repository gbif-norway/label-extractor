from minio import Minio
from helpers import process_image
import os

client = Minio(os.getenv('MINIO_URI'), access_key=os.getenv('MINIO_ACCESS_KEY'), secret_key=os.getenv('MINIO_SECRET_KEY'))

with client.listen_bucket_notification(os.getenv('MINIO_SOURCE_BUCKET'), events=["s3:ObjectCreated:*"]) as events:
    for event in events:
        for record in event['Records']:
            obj = record['s3']['object']
            print(obj)
            if obj['contentType'] == 'image/jpeg' or obj['contentType'] == 'image/tiff':
                process_image(obj['key'])
