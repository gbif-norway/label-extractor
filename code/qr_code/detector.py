import uuid
import cv2
import skimage
from pyzbar.pyzbar import decode

def extract_qr(image_uri):
    img = skimage.io.imread(image_uri)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    min_dim = min(img.shape[:2])
    block_size = int(min_dim/3)
    block_size += 0 if block_size%2 == 1 else 1 # blockSize should be odd
    image_bw = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, 2)

    qr_data = decode(image_bw)

    if not len(qr_data):
        raise Exception(f'No QR codes detected in {image_uri}')

    codes = {x.data.decode('utf-8').split('/')[-1] for x in qr_data}
    if len(codes) > 2:
        raise Exception(f'More than 2 QR codes/barcodes detected in {image_uri} - {codes}')

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
