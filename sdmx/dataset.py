import io
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from xml.dom import pulldom
from . import dsd, xmlpull
    

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
    if dsd_fileobj is None:
        default_dsd_reader = None
    else:
        default_dsd_reader = dsd.reader(fileobj=dsd_fileobj)
    
    class MessageReader(object):
        def __init__(self, event_stream, dsd_fetcher):
            self._event_stream = event_stream
            self._dsd_fetcher = dsd_fetcher
        
        def datasets(self):
            while True:
                dataset_node = parser.seek_dataset_node(self._event_stream)
                yield self._read_dataset_element(dataset_node)
            
        def _read_dataset_element(self, dataset_node):
            key_family = self._key_family(dataset_node)
            return DatasetReader(self._event_stream, dataset_node, self._dsd_fetcher, key_family)
        
        def _key_family(self, dataset_node):
            dsd_reader = self._dsd_reader(dataset_node)
            return KeyFamily(
                parser.key_family_for_dataset(self._event_stream, dataset_node, dsd_reader),
                dsd_reader,
            )
            
        def _dsd_reader(self, dataset_node):
            key_family_uri = dataset_node.getAttribute("keyFamilyURI")
            if key_family_uri is None:
                return default_dsd_reader
            else:
                return self._dsd_fetcher.fetch(key_family_uri)

    class DatasetReader(object):
        def __init__(self, event_stream, node, dsd_fetcher, key_family):
            self._event_stream = event_stream
            self._node = node
            self._dsd_fetcher = dsd_fetcher
            self._key_family = key_family
        
        def key_family(self):
            return self._key_family
        
        def series(self):
            key_family = self.key_family()
            while True:
                series_node, key = parser.seek_series_node(self._event_stream)
                yield self._read_series_element(key_family, series_node, key)
        
        def _read_series_element(self, key_family, series_node, key):
            return SeriesReader(key_family, series_node, key)


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
            
            return concept.name(lang=lang), self._describe_code(dimension.code_list_id(), code_value, lang=lang)
        
        def _describe_code(self, code_list_id, code_value, lang):
            code_list = self._dsd_reader.code_list(code_list_id)
            descriptions = []
            while code_value is not None:
                code = code_list.code(code_value.strip())
                description = code.description(lang=lang)
                descriptions.append(description)
                code_value = code.parent_code_id()
            
            return list(reversed(descriptions))
        
        def _find_dimension(self, concept_ref):
            for dimension in self._key_family_reader.dimensions():
                if dimension.concept_ref() == concept_ref:
                    return dimension


    class SeriesReader(object):
        def __init__(self, key_family, element, series_key):
            self._key_family = key_family
            self._element = element
            self._series_key = series_key
            
        def describe_key(self, lang):
            return self._key_family.describe_key(self._series_key, lang=lang)
        
        def observations(self, lang=None):
            observations = parser.read_observations(self._key_family, self._element)
            time_dimension = self._key_family.time_dimension()
            time_code_list_id = time_dimension.code_list_id()
            if time_code_list_id:
                if not lang:
                    raise ValueError("Observation time uses code list, but language is not specified")
                
                def describe_time_code(code):
                    codes = self._key_family._describe_code(time_code_list_id, code, lang=lang)
                    if len(codes) > 1:
                        raise ValueError("Time value has parent, case not handled")
                    else:
                        code, = codes
                        return code
                
                return [
                    Observation(time=describe_time_code(observation.time), value=observation.value)
                    for observation in observations
                ]
            else:
                return observations

    dsd_fetcher = DsdFetcher(requests)
    return MessageReader(xmlpull.EventStream(pulldom.parse(fileobj)), dsd_fetcher=dsd_fetcher)
