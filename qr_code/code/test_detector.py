import unittest
from detector import extract_qrs
import os

class QRTests(unittest.TestCase):
    IMG_FOLDER = 'test_cases'

    def test_2_qr_code_images(self):
        uuid, barcode = extract_qrs(os.path.join(self.IMG_FOLDER, '2_qr_codes_eg_1.jpg'))
        self.assertEqual(uuid, '9e952a9c-cca3-4baa-9f7a-e87c9b274706')
        self.assertEqual(barcode, 'Khatlon087')
        uuid, barcode = extract_qrs(os.path.join(self.IMG_FOLDER, '2_qr_codes_eg_2.jpg'))
        self.assertEqual(uuid, 'fc4e2049-f661-45d2-8a35-e32b0aa3ae61')
        self.assertEqual(barcode, 'Khatlon049')
        uuid, barcode = extract_qrs(os.path.join(self.IMG_FOLDER, '2_qr_codes_eg_3.jpg'))
        self.assertEqual(uuid, 'cc1ae5c6-a502-4b3a-a414-ddd786d50270')
        self.assertEqual(barcode, 'Khatlon052')

    def test_1_qr_code_image(self):
        uuid, barcode = extract_qrs(os.path.join(self.IMG_FOLDER, '1_qr_code_eg_1.jpg'))
        self.assertEqual(uuid, '11e6ae8b-95c6-4815-99c0-37defdf9b051')
        self.assertEqual(barcode, None)

    def test_1_qr_code_image_sideways(self):
        uuid, barcode = extract_qrs(os.path.join(self.IMG_FOLDER, '1_qr_code_eg_2.jpg'))
        self.assertEqual(uuid, 'bacb59d2-a309-4fe0-bc19-e77b0c413b08')
        self.assertEqual(barcode, None)

    def test_1_qr_code_image_in_lower_half(self):
        uuid, barcode = extract_qrs(os.path.join(self.IMG_FOLDER, '1_qr_code_eg_3.jpg'))
        self.assertEqual(uuid, '8c091b2a-32d4-4a80-b69a-bb3cf8ef5d19')
        self.assertEqual(barcode, None)

if __name__ == "__main__":
    unittest.main()
