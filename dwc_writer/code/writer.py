import logging
import os
from datetime import datetime
import pandas as pd
from minio import Minio
from minio.commonconfig import CopySource

def uuid_already_exists(source, uuid):
    if 'occurrenceID' in source.columns:
        return uuid in source['occurrenceID'].values
    else:
        raise Exception(f'No occurrence ID in source file {source}')

def append_to_source_file(source, target_source_path, dwc):
    dwc['modified'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    appended = pd.concat([source, pd.DataFrame([dwc])])

    appended.to_csv('/srv/code/source.txt', encoding='utf-8', index=False) # appended.iloc[-1:].to_csv('/srv/code/source.txt', encoding='utf-8', index=False, header=False)
    logging.info(f'Appended: {dwc}')

    client = Minio(os.getenv('MINIO_URI'), access_key=os.getenv('MINIO_ACCESS_KEY'), secret_key=os.getenv('MINIO_SECRET_KEY'))
    return client.fput_object(os.getenv('MINIO_IPT_BUCKET'), target_source_path, '/srv/code/source.txt', content_type='text/plain')

def get_ipt_source_file(path):
    source_file_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_IPT_BUCKET')}/{path}"
    try:
        return pd.read_csv(source_file_uri, dtype='str')
    except Exception as e:
        raise Exception(f'Problem with IPT source file {source_file_uri} - {e}')

def move_and_rename(image_path, new_image_path):
    client = Minio(os.getenv('MINIO_URI'), access_key=os.getenv('MINIO_ACCESS_KEY'), secret_key=os.getenv('MINIO_SECRET_KEY'))
    client.copy_object(os.getenv('MINIO_TARGET_BUCKET'), new_image_path, CopySource(os.getenv('MINIO_SOURCE_BUCKET'), image_path))
    client.remove_object(os.getenv('MINIO_SOURCE_BUCKET'), image_path)
