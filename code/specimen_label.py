import cyrtranslit 
import re
import nltk
import numpy as np
import pickle

with open('/srv/code/genera.pkl', 'rb') as f:
    GENERA = pickle.load(f)

class SpecimenLabel:
    def __init__(self, verbatim, institution, genus, catalog_number, uuid, associated_media_uri):
        self.label_contents = verbatim
        self.dets = self._extract_dets()  # Determinations, how are we supposed to handle these in dwc?
        
        verbatim = verbatim.replace('\n', '#')
        self.dwc = {
            'institutionCode': institution,
            'catalogNumber': catalog_number,
            'genus': genus,
            'occurrenceID': uuid,
            'associatedMedia': associated_media_uri,
            'dynamicProperties': f"verbatimTranscription: {verbatim} | verbatimTransliteration: {cyrtranslit.to_latin(verbatim, 'ru')}"
        }
        self.dwc['scientificName'] = self._extract_scientific_name(genus)
        self.dwc['minimumElevationInMeters'], self.dwc['maximumElevationInMeters'], self.dwc['verbatimElevation'] = self._extract_elevation()
        self.dwc['recordNumber'] = self._extract_record_number()
        self.dwc['year'] = self._extract_year() # self.dwc['month'],  self.dwc['day'], self.dwc['verbatimEventDate']
        self.dwc['recordedBy'] = None # https://unbiased-coder.com/extract-names-python-nltk/ ?
        self.dwc['verbatimLocality'] = self.label_contents.replace('\n', '#')

    def _extract_dets(self):
        return None

    def _extract_scientific_name(self, genus):
        lines = re.split('\n', self.label_contents)
        for line in lines:
            words = re.split('\s', re.sub('\s+', ' ', re.sub('[\d\.\:\;]', '', line)).strip())
            if words[0] == genus:
                self.label_contents = self.label_contents.split(line)[1]
                return ' '.join(words)

        # Fuzzy
        distances = []
        for line in lines:
            words = re.split('\s', re.sub('\s+', ' ', re.sub('[\d\.\:\;]', '', line)).strip())
            distances.append({'distance': nltk.edit_distance(genus, words[0]), 'words': words, 'line': line})

        closest_line = min(distances, key=lambda x: x['distance'])
        if closest_line['distance'] < 2:
            self.label_contents = self.label_contents.split(closest_line)[1]
            return genus + ' ' + ' '.join(closest_line['words'][1:])

        # Then genus is probably wrong
        for line in lines:
            words = re.split('\s', re.sub('\s+', ' ', re.sub('[\d\.\:\;]', '', line)).strip())
            if words[0] in GENERA:
                self.dwc['genus'] = words[0]
                self.label_contents = self.label_contents.split(line)[1]
                return ' '.join(words)

        distances = []
        for line in lines:
            words = re.split('\s', re.sub('\s+', ' ', re.sub('[\d\.\:\;]', '', line)).strip())
            word_ds = []
            for genus in GENERA:
                word_ds.append(nltk.edit_distance(genus, words[0]))
            wd_i = np.argmin(word_ds, 0)
            distances.append({'genus': GENERA[wd_i], 'distance': word_ds[wd_i], 'line': line, 'words': words})

        closest_line = min(distances, key=lambda x: x['distance'])
        if closest_line['distance'] < 2:
            self.dwc['genus'] = closest_line['genus']
            self.label_contents = self.label_contents.split(line)[1]
            return self.dwc['genus'] + ' ' + ' '.join(closest_line['words'][1:])

        print('no scientific name found')
        return None

    def _extract_elevation(self):
        numbers = '((\d[\d\s]*)*(\s*-([\d\s]+))?)\s*(([mм])|(ft))?\s*'
        matches = re.search('alt(itude)?[\.\s\:]*' + numbers, self.label_contents, re.IGNORECASE)
        if matches:
            if matches.group(2) is not None:
                self.label_contents = self.label_contents.replace(matches.group(0), '')
                return matches.group(2), matches.group(4), matches.group(0).strip()

        matches = re.search('\s' + numbers, self.label_contents, flags=re.IGNORECASE|re.UNICODE)
        if matches:
            self.label_contents = self.label_contents.replace(matches.group(0), '')
            if matches.group(2) is not None:
                if matches.group(5):  # meters
                    return matches.group(2), matches.group(4), matches.group(0).strip()
                else:
                    return None, None, matches.group(0).strip()

        return None, None, None

    def _extract_record_number(self):
        matches = re.search('(no|№)[\.\s\:]*(\d+)', self.label_contents, re.IGNORECASE)
        if matches:
            self.label_contents = self.label_contents.replace(matches.group(0), '')
            return matches.group(2)

    def _extract_year(self):
        matches = re.search('\n[\s\n\:\.]?((1[789][0-9]|20[0-3])\d)', self.label_contents)
        if matches:
            self.label_contents = self.label_contents.replace(matches.group(0), '')
            return matches.group(1)
