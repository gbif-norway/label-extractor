from minio import Minio
from minio.commonconfig import CopySource
from specimen_label import SpecimenLabel
from google.cloud import vision
import os
import logging
from pyzbar.pyzbar import decode
import skimage
import pandas as pd
from datetime import datetime
import uuid
import requests
import time
import io

def process_image(image_path):
    log = logging.getLogger(__name__)
    log.info(f'Processing image - {image_path}')
    institution, genus, original_image_name = image_path.split('/')

    image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_SOURCE_BUCKET')}/{image_path}"
    uuid, catalog_number = extract_qr(image_uri)
    new_image_path = f"{os.getenv('MINIO_TARGET_PREFIX')}/{institution}/{uuid}.jpg"
    new_image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_TARGET_BUCKET')}/{new_image_path}"

    if requests.get(image_uri).status_code == 200:
        time.sleep(5)  # Sometimes google is slow
        ocr_text = gv_ocr(image_uri, log) 
    else:
        Exception(f'File has been removed {image_uri}')
    
    label = SpecimenLabel(sort_and_flatten_ocr(ocr_text), institution, genus, catalog_number, uuid, new_image_uri)
    if append_to_ipt_source_file(institution, label.dwc):
        move_and_rename(image_path, new_image_path)

def extract_qr(image_uri):
    img = skimage.io.imread(image_uri)
    qr_data = decode(img)
    if not len(qr_data):
        Exception(f'No QR codes detected in {image_uri}')

    codes = {x.data.decode('utf-8').split('/')[-1] for x in qr_data}
    if len(codes) != 2:
        Exception(f'Incorrect number of QR codes/barcodes detected in {image_uri} - {codes}')

    uuid = next((x for x in codes if is_uuid4(x)), False)
    if not uuid:
        Exception(f'No UUID detected in {image_uri} - {codes}')
    codes.remove(uuid)

    return uuid, codes.pop()

def is_uuid4(test_uuid, version=4):
    try:
        return uuid.UUID(test_uuid).version == version
    except ValueError:
        return False

def gv_ocr(image_uri, log):
    gvclient = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri
    response = gvclient.document_text_detection(image=image)

    if response.error.code:
        log.error(f'Error from Google Cloud Vision - {response.error}')
        with io.open(image_uri, 'rb') as image_file:
                content = image_file.read()
                image = vision.Image(content=content)
                response = gvclient.document_text_detection(image=image)
                if response.error.code:
                    raise Exception(f"Error from Google Cloud Vision - {response.error}")
        
    return response.full_text_annotation

def sort_and_flatten_ocr(document):
    blocks = []
    for page in document.pages:
        for block in page.blocks:
            ps = []
            b = {'top': min(block.bounding_box.vertices[0].y, block.bounding_box.vertices[1].y)}
            for paragraph in block.paragraphs:
                ws = []
                for word in paragraph.words:
                    ws.append(''.join([l.text for l in word.symbols]))
                ps.append(' '.join(ws))
            b['text'] = '\n'.join(ps)
            blocks.append(b)
    sorted_blocks = sorted(blocks, key=lambda x: x['top'])
    return '\n'.join([b['text'] for b in sorted_blocks])

def append_to_ipt_source_file(institution, dwc):
    institution = 'test'
    path = f'resources/{institution.lower()}/sources'
    source = pd.read_csv(f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_IPT_BUCKET')}/{path}/source.txt", dtype='str')
    
    if 'occurrenceID' in source.columns:
        if dwc['occurrenceID'] not in source['occurrenceID'].values:
            dwc['modified'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            appended = pd.concat([source, pd.DataFrame([dwc])])
            appended.to_csv('/srv/code/source.txt', encoding='utf-8', index=False) # appended.iloc[-1:].to_csv('/srv/code/source.txt', encoding='utf-8', index=False, header=False)

            client = Minio(os.getenv('MINIO_URI'), access_key=os.getenv('MINIO_ACCESS_KEY'), secret_key=os.getenv('MINIO_SECRET_KEY'))
            return client.fput_object(os.getenv('MINIO_IPT_BUCKET'), f'{path}/source.txt', '/srv/code/source.txt', content_type='text/plain')
        else:
            Exception(f"Duplicate occurrence ID: {institution} - {path}, {dwc['occurrenceID']}")
    else:
        Exception(f"No occurrence ID in source file: {institution} - {path}, {source.columns}")

def move_and_rename(image_path, new_image_path):
    client = Minio(os.getenv('MINIO_URI'), access_key=os.getenv('MINIO_ACCESS_KEY'), secret_key=os.getenv('MINIO_SECRET_KEY'))
    # metadata={'original_filename': image_path}, metadata_directive='REPLACE'
    client.copy_object(os.getenv('MINIO_TARGET_BUCKET'), new_image_path, CopySource(os.getenv('MINIO_SOURCE_BUCKET'), image_path))
    client.remove_object(os.getenv('MINIO_SOURCE_BUCKET'), image_path)
