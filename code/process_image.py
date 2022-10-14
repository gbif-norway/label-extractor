from label_dwc.specimen_label import SpecimenLabel
import os
import logging
import requests
from qr_code.detector import extract_qr
from label_dwc import writer
from gapi_wrapper import vision, translate

def process_image(image_path):
    logging.warning(f'Processing image - {image_path}')
    institution, genus, original_image_name = image_path.split('/')

    image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_SOURCE_BUCKET')}/{image_path}"
    uuid = extract_qr(image_uri)
    logging.info('Extracted QR codes')
    
    target_source_path = f'resources/{institution.lower()}/sources/source.txt'
    target_source_file = writer.get_ipt_source_file(target_source_path)
    logging.info('Retrieved IPT source file')
    
    if writer.uuid_already_exists(target_source_file, uuid):
        raise Exception(f'UUID already exists in source file darwin core - {uuid} in {image_path}')
    
    new_image_path = f"{os.getenv('MINIO_TARGET_PREFIX')}/{institution}/{uuid}.jpg"
    new_image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_TARGET_BUCKET')}/{new_image_path}"

    img = requests.get(image_uri)
    if img.status_code == 200:
        ocr_text = vision.gv_ocr(img.content) 
    else:
        raise Exception(f'File has been removed {image_uri}')
    logging.info(f'OCR success, results: {ocr_text}')
    
    label = SpecimenLabel(ocr_text, institution, genus, uuid, uuid, new_image_uri)
    logging.info(f'Label object populated created: {label.dwc}')
    
    label.fill_translated_fields(translate.gtranslate(' '.join(label.label_lines)))
    logging.info(f'Translated parts of label filled: {label.dwc}')

    if writer.append_to_source_file(target_source_file, target_source_path, label.get_ipt_dwc()):
        logging.info('Row appended to source file')
        writer.move_and_rename(image_path, new_image_path)
        logging.info('File moved')
    
    logging.warning(f'Complete - {image_path}')
