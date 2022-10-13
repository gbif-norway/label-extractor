import cyrtranslit 
import logging
from label_dwc import extractor
import json


class SpecimenLabel:
    def __init__(self, verbatim, institution, genus, catalog_number, uuid, associated_media_uri):
        self.verbatim = verbatim
        self.translation = None

        self.label_lines = extractor.lines(verbatim)
        i, verbatim_id = extractor.verbatim_identification(self.label_lines, genus)

        if not verbatim_id:
            i, verbatim_id, genus = extractor.verbatim_identification_no_genus(self.label_lines)
        if i:
            self.label_lines = self.label_lines[i:]

        scientific_name = genus
        if verbatim_id:
            name_parts = verbatim_id.split(' ')
            if len(name_parts) > 1:
                scientific_name += ' ' + name_parts[1]
        
        elevation = extractor.elevation(self.label_lines)
        min, max = extractor.min_max_elevation_in_meters(elevation)

        self.dwc = {
            'institutionCode': institution,
            'catalognumber': catalog_number,
            'genus': genus,
            'occurrenceID': uuid,
            'associatedMedia': associated_media_uri,
            'verbatimIdentification': verbatim_id,
            'scientificName': scientific_name,
            'minimumElevationInMeters': min,
            'maximumElevationInMeters': max,
            'verbatimElevation': elevation,
            'recordNumber': extractor.record_number(self.label_lines),
            'year': extractor.year(self.label_lines),
            'dynamicProperties': {
                'verbatimTranscription': extractor.ipt_friendly_string(self.verbatim),
                'verbatimTransliteration': cyrtranslit.to_latin(extractor.ipt_friendly_string(self.verbatim), 'ru'),
            }   
        }

    def get_ipt_dwc(self):
        dwc = self.dwc
        dwc['dynamicProperties'] = json.dumps(self.dwc['dynamicProperties'], ensure_ascii=False).encode('utf8').decode()
        dwc['dynamicProperties'].replace('\n', '#').replace(',', ' ').replace('\t', '')
        return dwc

    def fill_translated_fields(self, translated):
        self.translation = translated
        self.dwc['dynamicProperties']['verbatimTranslation'] = extractor.ipt_friendly_string(translated)
        self.dwc['recordedBy'] = extractor.names(extractor.lines(translated))
        self.dwc['country'] = extractor.country(extractor.lines(translated))
