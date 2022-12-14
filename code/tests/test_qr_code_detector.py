import unittest
from qr_code.detector import extract_qr

class QRTests(unittest.TestCase):
    # def test_2_qr_code_images(self):
    #     qrs = extract_qr('tests/qr-code-cases/2_qr_codes_eg_1.jpg')
    #     self.assertEqual(qrs[0], '9e952a9c-cca3-4baa-9f7a-e87c9b274706')
    #     self.assertEqual(qrs[1], 'Khatlon087')
    #     qrs = extract_qr('tests/qr-code-cases/2_qr_codes_eg_2.jpg')
    #     self.assertEqual(qrs[0], 'fc4e2049-f661-45d2-8a35-e32b0aa3ae61')
    #     self.assertEqual(qrs[1], 'Khatlon049')
    #     qrs = extract_qr('tests/qr-code-cases/2_qr_codes_eg_3.jpg')
    #     self.assertEqual(qrs[0], 'cc1ae5c6-a502-4b3a-a414-ddd786d50270')
    #     self.assertEqual(qrs[1], 'Khatlon052')

    def test_1_qr_code_image(self):
        uuid = extract_qr('tests/qr-code-cases/1_qr_code_eg_1.jpg')
        self.assertEqual(uuid, '11e6ae8b-95c6-4815-99c0-37defdf9b051')

    def test_1_qr_code_image_sideways(self):
        uuid = extract_qr('tests/qr-code-cases/1_qr_code_eg_2.jpg')
        self.assertEqual(uuid, 'bacb59d2-a309-4fe0-bc19-e77b0c413b08')

    def test_1_qr_code_image_in_lower_half(self):
        uuid = extract_qr('tests/qr-code-cases/1_qr_code_eg_3.jpg')
        self.assertEqual(uuid, '8c091b2a-32d4-4a80-b69a-bb3cf8ef5d19')

if __name__ == "__main__":
    unittest.main()
