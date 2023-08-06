# -*- coding: utf-8 -*-

import unittest
import pdfparanoia

class AmericanSocietyForNutritionTestCase(unittest.TestCase):
    def test_amsocnut(self):
        file_handler = open("tests/samples/amsocnut/31e63a4ef65e16d66a97563966f1739a.pdf", "rb")
        content = file_handler.read()
        file_handler.close()

        output = pdfparanoia.plugins.AmericanSocietyForNutrition.scrub(content)
        fh = open("output.pdf", "wb")
        fh.write(output)
        fh.close()

        # FlateDecode should be replaced with a decompressed section
        #self.assertIn("\n19 0 obj\n<</Length 2862>>stream", output)

