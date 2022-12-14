from minio import Minio
from process_image import process_image
import os
import logging
from urllib3.exceptions import ReadTimeoutError

def listen():
    logging.info(f"Listening to {os.getenv('MINIO_URI')} / os.getenv('MINIO_SOURCE_BUCKET') ...")
    client = Minio(os.getenv('MINIO_URI'), access_key=os.getenv('MINIO_ACCESS_KEY'), secret_key=os.getenv('MINIO_SECRET_KEY'))

    try:
        with client.listen_bucket_notification(os.getenv('MINIO_SOURCE_BUCKET'), events=["s3:ObjectCreated:*"]) as events:
            for event in events:
                for record in event['Records']:
                    obj = record['s3']['object']
                    if obj['contentType'] == 'image/jpeg' or obj['contentType'] == 'image/tiff':
                        try:
                            logging.info(f'Processing {obj["key"]}')
                            process_image(obj['key'])
                        except Exception as e:
                            logging.error(f"Image processing failed - {obj['key']}. Error {e}")
    except ReadTimeoutError as e:
        logging.error('Python minio listen_bucket_notification timeout, restarting...')
        listen()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    listen()
    