import pika
from vision import gv_ocr
import os
import requests

def main():
    base_url = 'http://api.gbif.org/v1/occurrence/search'
    dataset_key = os.environ['GET_IMAGES_DATASETKEY']
    limit = os.environ.get('GET_IMAGES_LIMIT', 1)
    country = os.environ.get('COUNTRY', '*')
    kingdom = os.environ.get('GET_IMAGES_KINGDOM', 'Plantae')
    query_string = f"{base_url}?datasetKey={dataset_key}&limit={limit}&country={country}&kingdom={kingdom}&mediaType=StillImage&multimedia=true"

    response = requests.get(query_string)
    if response.status_code == requests.codes.ok:
        connection_params = pika.ConnectionParameters(host='localhost')
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        results = response.json().get('results')
        for result in results:
            if 'media' in result:
                message = {'occurrence_id': result['occurrenceID'],
                           'gbif_id': result['gbifID'],
                           'image_url': result['media'][0]['identifier']}

                channel.basic_publish(routing_key='gbif-api-get-images',
                                      body=message,
                                      properties=pika.BasicProperties(delivery_mode = 2))

if __name__ == '__main__':
    main()
