import io
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .xmlcommon import parse_xml, XmlNode
from . import dsd
    

class DsdFetcher(object):
    def __init__(self, requests):
        self._requests = requests
        self._cache = {}
    
    def fetch(self, url):
        if url not in self._cache:
            response = self._requests.get(url)
            fileobj = io.BytesIO()
            for buf in response.iter_content(16 * 1024):
                fileobj.write(buf)
            fileobj.flush()
            fileobj.seek(0)
            
            self._cache[url] = dsd.reader(fileobj)
        
        return self._cache[url]


class Observation(object):
    def __init__(self, time, value):
        self.time = time
        self.value = value


def data_message_reader(parser, fileobj, requests=None, dsd_fileobj=None):
    class DatasetsReader(object):
        def __init__(self, tree, dsd_fetcher):
            self._tree = tree
            self._dsd_fetcher = dsd_fetcher
        
        def datasets(self):
            return map(
                self._read_dataset_element,
                parser.get_dataset_elements(self._tree),
            )
            
        def _read_dataset_element(self, element):
            return DatasetReader(element, self._dsd_fetcher)

    class DatasetReader(object):
        def __init__(self, element, dsd_fetcher):
            self._element = element
            self._dsd_fetcher = dsd_fetcher
        
        def key_family(self):
            dsd_reader = self._dsd_reader()
            return KeyFamily(
                parser.key_family_for_dataset(self._element, dsd_reader),
                dsd_reader,
            )
        
        def series(self):
            key_family = self.key_family()
            return map(
                lambda element: self._read_series_element(key_family, element),
                parser.get_series_elements(self._element),
            )
            
        def _dsd_reader(self):
            key_family_uri = self._element.get("keyFamilyURI")
            if key_family_uri is None:
                return dsd.reader(fileobj=dsd_fileobj)
            else:
                return self._dsd_fetcher.fetch(key_family_uri)
        
        def _read_series_element(self, key_family, element):
            return SeriesReader(key_family, element)


    class KeyFamily(object):
        def __init__(self, key_family_reader, dsd_reader):
            self._key_family_reader = key_family_reader
            self._dsd_reader = dsd_reader
        
        def name(self, lang):
            return self._key_family_reader.name(lang=lang)
        
        def describe_dimensions(self, lang):
            return [
                self._dsd_reader.concept(dimension.concept_ref()).name(lang=lang)
                for dimension in self._key_family_reader.dimensions()
            ]
        
        def describe_key(self, key, lang):
            key_lookup = dict(key)
            return OrderedDict(
                self._describe_value(dimension, key_lookup[dimension.concept_ref()], lang=lang)
                for dimension in self._key_family_reader.dimensions()
            )
            
        def time_dimension(self):
            return self._key_family_reader.time_dimension()
            
        def primary_measure(self):
            return self._key_family_reader.primary_measure()
        
        def _describe_value(self, dimension, code_value, lang):
            concept = self._dsd_reader.concept(dimension.concept_ref())
            code_list = self._dsd_reader.code_list(dimension.code_list_id())
            
            return concept.name(lang=lang), self._describe_code(code_list, code_value, lang=lang)
        
        def _describe_code(self, code_list, code_value, lang):
            descriptions = []
            while code_value is not None:
                code = code_list.code(code_value)
                description = code.description(lang=lang)
                descriptions.append(description)
                code_value = code.parent_code_id()
            
            return list(reversed(descriptions))
        
        def _find_dimension(self, concept_ref):
            for dimension in self._key_family_reader.dimensions():
                if dimension.concept_ref() == concept_ref:
                    return dimension


    class SeriesReader(object):
        def __init__(self, key_family, element):
            self._key_family = key_family
            self._element = element
            
        def describe_key(self, lang):
            series_key = parser.series_key(self._element)
            return self._key_family.describe_key(series_key, lang=lang)
        
        def observations(self):
            return parser.read_observations(self._key_family, self._element)

    tree = XmlNode(parse_xml(fileobj).getroot())
    dsd_fetcher = DsdFetcher(requests)
    return DatasetsReader(tree, dsd_fetcher=dsd_fetcher)
