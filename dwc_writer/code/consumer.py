import pika

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
