import uuid
import cv2
import skimage
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import pika

def extract_qrs(image_uri):
    im = skimage.io.imread(image_uri)
    cvgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret, bw_im = cv2.threshold(cvgray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    qr_data = decode(bw_im, symbols=[ZBarSymbol.QRCODE])
    
    if not len(qr_data):
        raise Exception(f'No QR codes detected in {image_uri}')

    codes = {x.data.decode('utf-8').split('/')[-1] for x in qr_data}
    if len(codes) > 2:
        raise Exception(f'More than 2 QR codes/barcodes detected in {image_uri} - {codes}')

    uuid = None
    barcode = None
    for x in codes:
        if is_uuid4(x):
            uuid = x
        else:
            barcode = x

    if not uuid:
        raise Exception(f'No UUID detected in {image_uri} - {codes}')
 
    return uuid, barcode

def is_uuid4(test_uuid, version=4):
    try:
        return uuid.UUID(test_uuid).version == version
    except ValueError:
        return False

def on_message(ch, method, properties, body):
    message = body.decode('UTF-8')
    print(message)

def main():
    connection_params = pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue='testing')

    channel.basic_consume(queue='testing', on_message_callback=on_message, auto_ack=True)

    print('Subscribed to testing, waiting for messages...')
    channel.start_consuming()

if __name__ == '__main__':
    main()
