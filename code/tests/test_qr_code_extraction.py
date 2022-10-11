import cv2 
import skimage
from pathlib import Path
import unittest
from pyzbar.pyzbar import decode

class QRTests(unittest.TestCase):
    def test_all_qrs_together(self):
        all_qr_tests = Path('tests/qr-code-cases').glob('*.jpg')

        for qr in all_qr_tests:
            cvimg = skimage.io.imread(qr)
            grey = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
            min_dim = min(cvimg.shape[:2])
            block_size = int(min_dim/3)
            block_size += 0 if block_size%2 == 1 else 1 # blockSize should be odd
            image_bw = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, 2)

            qr_data = decode(image_bw)
            self.assertGreaterEqual(len(qr_data), 1)

if __name__ == "__main__":
    unittest.main()
