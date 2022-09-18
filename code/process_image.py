from specimen_label import SpecimenLabel
import os
import logging
import requests
import helpers

def process_image(image_path):
    logging.warning(f'Processing image - {image_path}')
    institution, genus, original_image_name = image_path.split('/')

    image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_SOURCE_BUCKET')}/{image_path}"
    uuid, catalog_number = helpers.extract_qr(image_uri)
    logging.info('Extracted QR codes')
    
    target_source_path = f'resources/{institution.lower()}/sources/source.txt'
    target_source_file = helpers.get_ipt_source_file(target_source_path)
    logging.info('Retrieved IPT source file')
    
    if helpers.uuid_already_exists(target_source_file, uuid):
        raise Exception(f'UUID already exists in source file darwin core - {uuid} in {image_path}')
    
    new_image_path = f"{os.getenv('MINIO_TARGET_PREFIX')}/{institution}/{uuid}.jpg"
    new_image_uri = f"https://{os.getenv('MINIO_URI')}/{os.getenv('MINIO_TARGET_BUCKET')}/{new_image_path}"

    if requests.get(image_uri).status_code == 200:
        ocr_text = helpers.gv_ocr(image_uri) 
    else:
        raise Exception(f'File has been removed {image_uri}')
    logging.info(f'OCR success, results: {ocr_text}')
    
    label = SpecimenLabel(ocr_text, institution, genus, catalog_number, uuid, new_image_uri)
    logging.info(f'Label object populated created: {label.dwc}')
    
    label.fill_translated_fields(helpers.gtranslate(' '.join(label.label_lines)))
    logging.info(f'Translated parts of label filled: {label.dwc}')

    if helpers.append_to_source_file(target_source_file, target_source_path, label.get_ipt_dwc()):
        logging.info('Row appended to source file')
        helpers.move_and_rename(image_path, new_image_path)
        logging.info('File moved')
    
    logging.warning(f'Complete - {image_path}')
