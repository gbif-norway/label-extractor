from specimen_label import SpecimenLabel
import os
import logging
import requests
import helpers

def process_image(image_path):
    log = logging.getLogger(__name__)
    log.info(f'Processing image - {image_path}')
    institution, genus, original_image_name = image_path.split('/')

    image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_SOURCE_BUCKET')}/{image_path}"
    uuid, catalog_number = helpers.extract_qr(image_uri)
    log.debug('Extracted QR code')

    target_source_path = f'resources/test/sources/source.txt' # f'resources/{institution.lower()}/sources/source.txt'
    target_source_file = helpers.get_ipt_source_file(target_source_path)
    log.debug('Retrieved IPT source file')
    
    if helpers.uuid_already_exists(target_source_file, uuid):
        raise Exception(f'UUID already exists in source file darwin core - {uuid} in {image_path}')
    
    new_image_path = f"{os.getenv('MINIO_TARGET_PREFIX')}/{institution}/{uuid}.jpg"
    new_image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_TARGET_BUCKET')}/{new_image_path}"

    if requests.get(image_uri).status_code == 200:
        ocr_text = helpers.gv_ocr(image_uri) 
    else:
        raise Exception(f'File has been removed {image_uri}')
    log.debug('OCR success')

    label = SpecimenLabel(ocr_text, institution, genus, catalog_number, uuid, new_image_uri)
    log.debug('Label retrieved')

    if helpers.append_to_source_file(target_source_file, target_source_path, label.dwc):
        log.debug('Row appended to source file')
        helpers.move_and_rename(image_path, new_image_path)
        log.debug('File moved')
    
    log.info(f'Complete - {image_path}')
