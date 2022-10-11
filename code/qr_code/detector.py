import uuid
import cv2
import skimage
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol

def extract_qr(image_uri):
    img = skimage.io.imread(image_uri)

    # try 1
    im = cv2.imread(image_uri, cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(im, (5, 5), 0)
    ret, bw_im = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    qr_data = decode(bw_im, symbols=[ZBarSymbol.QRCODE])
    
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
