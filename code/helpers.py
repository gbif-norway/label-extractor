from tkinter import E
from minio import Minio
from minio.commonconfig import CopySource
import io
from pyzbar.pyzbar import decode
import skimage
import pandas as pd
from datetime import datetime
import uuid
from google.cloud import vision
import os
from google.cloud import translate_v2 as translate
import logging

def extract_qr(image_uri):
    img = skimage.io.imread(image_uri)
    qr_data = decode(img)
    if not len(qr_data):
        raise Exception(f'No QR codes detected in {image_uri}')

    codes = {x.data.decode('utf-8').split('/')[-1] for x in qr_data}
    if len(codes) != 2:
        raise Exception(f'Incorrect number of QR codes/barcodes detected in {image_uri} - {codes}')

    uuid = next((x for x in codes if is_uuid4(x)), False)
    if not uuid:
        raise Exception(f'No UUID detected in {image_uri} - {codes}')
    codes.remove(uuid)

    return uuid, codes.pop()

def is_uuid4(test_uuid, version=4):
    try:
        return uuid.UUID(test_uuid).version == version
    except ValueError:
        return False

def gv_ocr(image_uri):
    gvclient = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri
    logging.info(f'Attempting to ocr via Google Cloud Vision - {image_uri}')
    response = gvclient.document_text_detection(image=image)

    if response.error.code:
        logging.error(f'Error from Google Cloud Vision fetching remotely - {response.error}')
        with io.open(image_uri, 'rb') as image_file:
                content = image_file.read()
                image = vision.Image(content=content)
                response = gvclient.document_text_detection(image=image)
                if response.error.code:
                    raise Exception(f"Error from Google Cloud Vision - {response.error}")
    
    logging.info(f'Successfully ocred')
    return sort_and_flatten(response.full_text_annotation)

def sort_and_flatten(document):
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
    cutoff_index = next((i for i, el in enumerate(sorted_blocks) if cutoff(el['text'])), len(sorted_blocks))
    logging.info(f'Processing OCRed text and discarded from block {cutoff_index}: {sorted_blocks[cutoff_index:]}')

    remaining = '\n'.join([b['text'] for b in sorted_blocks[0:cutoff_index]])
    logging.info(f'Remaining text: {remaining}')
    return remaining

def cutoff(text):
    triggers = ['MADE IN CHINA', 'HORSE BRAND', 'Plantae Tadshikistanicae', 'BRAND NO . 1001']
    for t in triggers:
        if t in text:
            return True
    return False

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

def gtranslate(text):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language='en')

    logging.info(u"Text: {}".format(result["input"]))
    logging.info(u"Translation: {}".format(result["translatedText"]))
    logging.info(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
    return result["translatedText"]

