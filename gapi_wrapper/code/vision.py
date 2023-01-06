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
    return response.full_text_annotation

def sort_and_flatten(document):
    blocks = []
    for page in document.pages:
        for block in page.blocks:
            ps = []
            b = {'top': min(block.bounding_box.vertices[0].y, block.bounding_box.vertices[1].y)}
            for paragraph in block.paragraphs:
                ws = []
                for word in paragraph.words:
                    ws.append(''.join([l.text for l in word.symbols]))
                ps.append(' '.join(ws))
            b['text'] = '\n'.join(ps)
            blocks.append(b)

    sorted_blocks = sorted(blocks, key=lambda x: x['top'])
    cutoff_index = next((i for i, el in enumerate(sorted_blocks) if cutoff(el['text'])), len(sorted_blocks))
    logging.info(f'Processing OCRed text and discarded from block {cutoff_index}: {sorted_blocks[cutoff_index:]}')

    remaining = '\n'.join([b['text'] for b in sorted_blocks[0:cutoff_index]])
    logging.info(f'Remaining text: {remaining}')
    return remaining

def cutoff(text):  # We need a better way to take rulers out
    triggers = ['MADE IN CHINA', 'HORSE BRAND', 'Plantae Tadshikistanicae', 'BRAND NO . 1001']
    for t in triggers:
        if t in text:
            return True
    return False
