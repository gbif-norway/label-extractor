import pika
import json
from vision import gv_ocr

def on_message(ch, method, properties, body):
    message = json.loads(body.decode('UTF-8'))
    ocr_results = gv_ocr(message['occurrence_id'])

    ch.queue_declare(queue='gapi-vision', durable=True)
    ch.basic_publish(routing_key='gapi-vision',
                     body=json.dumps(ocr_results),
                     properties=pika.BasicProperties(delivery_mode = 2))

def main():
    connection_params = pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    #channel.queue_declare(queue='qr-scan', durable=True)
    #channel.basic_consume(queue='qr-scan', on_message_callback=on_message, auto_ack=True)
    channel.queue_declare(queue='gbif-api-get-images', durable=True)
    channel.basic_consume(queue='gbif-api-get-images', on_message_callback=on_message, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()
