import cyrtranslit 
import re
import nltk
import numpy as np
import pickle
import logging
from helpers import gtranslate, find_human_names
import pycountry
import json


with open('/srv/code/genera.pkl', 'rb') as f:
    GENERA = pickle.load(f)

class SpecimenLabel:
    def __init__(self, verbatim, institution, genus, catalog_number, uuid, associated_media_uri):
        self.label_contents = verbatim
        self.dets = self._extract_dets()  # Determinations, how are we supposed to handle these in dwc?
        
        self.dwc = {
            'institutionCode': institution,
            'catalogNumber': catalog_number,
            'genus': genus,
            'occurrenceID': uuid,
            'associatedMedia': associated_media_uri,
        }
        self.dwc['verbatimIdentification'] = self._extract_verbatim_identification(self.label_contents, genus)
        if self.dwc['verbatimIdentification']:
            self.dwc['scientificName'] = self.dwc['genus'] + ' ' + self.dwc['verbatimIdentification'].split(' ')[1]
        self.dwc['minimumElevationInMeters'], self.dwc['maximumElevationInMeters'], self.dwc['verbatimElevation'] = self._extract_elevation()
        self.dwc['recordNumber'] = self._extract_record_number()
        self.dwc['year'] = self._extract_year() # self.dwc['month'],  self.dwc['day'], self.dwc['verbatimEventDate']

        lines_for_translation = self.label_contents.split('Plantae Tadshikistan')[0].split('\n')
        translated = gtranslate(' '.join(lines_for_translation))
        self.dwc['recordedBy'] = self._extract_names(translated)
        self.dwc['country'] = self._extract_country(translated)

        dynamicProperties = {
            'verbatimTranscription': verbatim.replace('\n', '#'),
            'verbatimTransliteration': cyrtranslit.to_latin(verbatim.replace('\n', ' '), 'ru'),
            'verbatimTranslation': translated
        }
        self.dwc['dynamicProperties'] = json.dumps(dynamicProperties, ensure_ascii=False).encode('utf8').decode()

    def _extract_dets(self):
        return None

    def _extract_verbatim_identification(self, lines_text, genus):
        lines = re.split('\n', lines_text)
        first_words_per_line = [self._get_words(line)[0] for line in lines]
        
        # Usual scenario has the genus as the first word of the line containing the scientific name line
        for line_index, first_word in enumerate(first_words_per_line):
            if first_word.lower() == genus.lower():
                self.discard_text_above_main_label(lines[line_index])
                return ' '.join(self._get_words(lines[line_index]))
        
        # Sometimes scientific name is not the first word in a line, but is in the line somewhere
        for line in lines:
            if genus in line:
                self.discard_text_above_main_label(line)
                return ' '.join(self._get_words(line))
        
        # Fuzzy matching for first word in line, perhaps the given genus has a spelling mistake
        distances = [nltk.edit_distance(genus, word) for word in first_words_per_line]
        closest_distance, line_index = min((val, idx) for (idx, val) in enumerate(distances))
        if closest_distance < 3:
            self.discard_text_above_main_label(lines[line_index])
            name_parts = self._get_words(lines[line_index])
            name_parts[0] = genus
            return ' '.join(name_parts)

        # Then genus is probably just completely wrong, search for any line with a first word that is a genus
        for first_word, line_index in enumerate(first_words_per_line):
            if first_word in GENERA:
                self.dwc['genus'] = first_word
                self.discard_text_above_main_label(lines[line_index])
                return ' '.join(self._get_words(lines[line_index]))
        
        # Fuzzy match for any genus at any first word in a line
        distances = []
        for line_index, first_word in enumerate(first_words_per_line):
            word_distances = {}
            for genus in GENERA:
                word_distances[genus] = nltk.edit_distance(genus, first_word)
            closest_genus, closest_distance = min(word_distances.items(), key=lambda x: x[1])
            distances.append({'genus': closest_genus, 'distance': closest_distance, 'line_index': line_index})
        
        closest = min(distances, key=lambda x: x['distance'])
        if closest['distance'] < 3:
            li = closest['line_index']
            self.discard_text_above_main_label(lines[li])
            verbatim = ' '.join(self._get_words(lines[li]))
            verbatim = verbatim.replace(first_words_per_line[li], closest['genus'])
            self.dwc['genus'] = closest['genus']
            return verbatim
        
        log = logging.getLogger(__name__)
        log.error('No scientific name found.')
        return None

    def discard_text_above_main_label(self, line):
        self.label_contents = self.label_contents.split(line)[1]

    def _get_words(self, line):
        return re.split('\s', re.sub('\s+', ' ', re.sub('[^A-Za-z()\s]', '', line)).strip())

    def _extract_elevation(self):
        numbers = '((\d[\d\s]*)*(\s*-([\d\s]+))?)\s*(([mм])|(ft))?\s*'
        matches = re.search('alt(itude)?[\.\s\:]*' + numbers, self.label_contents, re.IGNORECASE)
        if matches:
            if matches.group(2):
                #self.label_contents = self.label_contents.replace(matches.group(0), '')
                return matches.group(2), matches.group(4), matches.group(0).strip()

        matches = re.search('\s' + numbers, self.label_contents, flags=re.IGNORECASE|re.UNICODE)
        if matches:
            if matches.group(2):
                if matches.group(5):  # meters
                    #self.label_contents = self.label_contents.replace(matches.group(0), '')
                    return matches.group(2), matches.group(4), matches.group(0).strip()
                else:
                    return None, None, matches.group(0).strip()

        return None, None, None

    def _extract_record_number(self):
        matches = re.search('(no|№)[\.\s\:]*(\d+)', self.label_contents, re.IGNORECASE)
        if matches:
            #self.label_contents = self.label_contents.replace(matches.group(0), ' ')
            return matches.group(2)

    def _extract_year(self):
        matches = re.search('\n[\s\n\:\.]?((1[789][0-9]|20[0-3])\d)', self.label_contents)
        if matches:
            #self.label_contents = self.label_contents.replace(matches.group(0), ' ')
            return matches.group(1)

    def _extract_names(self, text):
        collected = ['collected', 'coll.', 'coll:', 'collector']
        for phrase in collected:
            matches = re.search(phrase, text, re.IGNORECASE)
            if matches:
                return text.split(matches.group(0))[-1]
        return None
        #return find_human_names(text)
    
    def _extract_country(self, text):
        common_countries = ['Tajikistan', 'Afghanistan', 'China', 'Russia', 'Kazakhstan']
        for country in common_countries:
            if country.lower() in text.lower():
                return country
        
        for country in pycountry.countries:
            if country.name.lower() in text.lower():
                return country.name
