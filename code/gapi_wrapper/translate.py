import logging
from google.cloud import translate_v2 as translate

def gtranslate(text):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language='en')

    logging.info(u"Text: {}".format(result["input"]))
    logging.info(u"Translation: {}".format(result["translatedText"]))
    logging.info(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
    return result["translatedText"]
