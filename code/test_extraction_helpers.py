import unittest
import extraction_helpers as eh

class ExtranctionHelpers(unittest.TestCase):
    def test_verbatim_identification(self):
        tests = [
            'Herbarium БОТАНИКИ\nVulpia alopec\nCollected by A. Person',
            'Herbarium БОТАНИКИ\nБиришти, Vulpia alopec\nCollected by A. Person',
            'Herbarium БОТАНИКИ\nNulpia alopec\nCollected by A. Person',
            '\nNulpia alopec',
        ]
        for t in tests:
            line_index, verbatim_id = eh.verbatim_identification(eh.lines(t), 'Vulpia')
            self.assertEqual(verbatim_id, 'Vulpia alopec')
            self.assertEqual(line_index, 1)

    def test_verbatim_identification_no_genus(self):
        tests = [
            'БОТАНИКИ\nFreesia alopec\nCollected by A. Person',
            'БОТАНИКИ\nFreesia alopec\n',
            #'БОТАНИКИ\nFreesio alopec\n', Takes quite a long time to run
        ]
        for t in tests:
            line_index, verbatim_id, genus = eh.verbatim_identification_no_genus(eh.lines(t))
            self.assertEqual(line_index, 1)
            self.assertEqual(verbatim_id, 'Freesia alopec')
            self.assertEqual(genus, 'Freesia')

    def test_elevation(self):
        self.assertEqual(eh.elevation(eh.lines('Altitude 881 m')), '881 m')
        self.assertEqual(eh.elevation(eh.lines('Text text Alt: 881 m')), '881 m')
        self.assertEqual(eh.elevation(eh.lines('This species was collected at 881 m and ')), '881 m')
        self.assertEqual(eh.elevation(eh.lines('Alt. 881')), '881')
        self.assertEqual(eh.elevation(eh.lines('Alt: 881')), '881')
        self.assertEqual(eh.elevation(eh.lines('Alt - 881')), '881')
        self.assertEqual(eh.elevation(eh.lines('Alt- 881')), '881')
        self.assertEqual(eh.elevation(eh.lines('Alt 881ft')), '881ft')
        self.assertEqual(eh.elevation(eh.lines('A6232\nVolpin Myras qual\nБ.А. Федченко : 2\n915')), None)
        self.assertEqual(eh.elevation(eh.lines('Some text h- 1700')), '1700')
        self.assertEqual(eh.elevation(eh.lines('Some text h- 10')), None)

    def test_names(self):
        tests = [
            'coll. B. A. Sharipov and others\nVulpia',
        ]
        for t in tests:
            self.assertEqual(eh.names(eh.lines(t)), 'B. A. Sharipov and others')

    def test_get_latin_words(self):
        test = 'Хр . Ходжа - Казьян Vulpia persica, жски Alt. 499'
        expected = ['Vulpia', 'persica', 'Alt',]
        self.assertEqual(eh._get_latin_words(test), expected)

        test = ' Habitat: sandy ridge, Collector B. A. Sharipov '
        expected = ['Habitat', 'sandy', 'ridge', 'Collector', 'B', 'A', 'Sharipov']
        self.assertEqual(eh._get_latin_words(test), expected)


if __name__ == "__main__":
    unittest.main()
