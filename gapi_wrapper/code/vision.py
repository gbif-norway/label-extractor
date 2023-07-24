import logging
from google.cloud import vision

def gv_ocr(content):
    gvclient = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    logging.info(f'Attempting to ocr via Google Cloud Vision...')
    response = gvclient.document_text_detection(image=image)
    if response.error.code:
        raise Exception(f"Error from Google Cloud Vision - {response.error}")

    logging.info(f'Successfully ocred')
    return response
