import uuid
import cv2
import skimage
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from skimage.color import rgb2gray
from skimage import filters # threshold_otsu, threshold_isodata
from skimage.morphology import binary_dilation, binary_erosion

def extract_qr(image_uri):
    im = skimage.io.imread(image_uri)
    #grayscale = rgb2gray(im)
    	
    cvgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    height, width, dimensions = im.shape
    halved = cvgray[int(height/2):height, 0:width]
    ret, bw_im = cv2.threshold(halved, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    qr_data = decode(bw_im, symbols=[ZBarSymbol.QRCODE])

    #im = cv2.imread(image_uri, cv2.IMREAD_GRAYSCALE)
    #blur = cv2.GaussianBlur(grayscale, (5, 5), 0)
    # binaries = {
    #     'binary_otsu': halved > filters.threshold_otsu(halved),
    #     'binary_iso': halved > filters.threshold_isodata(halved),
    #     'binary_li': halved > filters.threshold_li(halved),
    #     'binary_local': halved > filters.threshold_local(halved),
    #     'binary_mean': halved > filters.threshold_mean(halved),
    #     'binary_min': halved > filters.threshold_minimum(halved),
    #     'binary_niblack': halved > filters.threshold_niblack(halved),
    #     'binary_sauvola': halved > filters.threshold_sauvola(halved),
    #     'binary_triangle': halved > filters.threshold_triangle(halved),
    #     'binary_yen': halved > filters.threshold_yen(halved)
    # }
    # for key, b in binaries.items():
    #     print(key)
    #     print(decode(b))
    
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
