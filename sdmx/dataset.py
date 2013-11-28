import io
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .xmlcommon import inner_text, parse_xml
from . import dsd


def reader(fileobj, requests=None):
    tree = XmlNode(parse_xml(fileobj))
    dsd_fetcher = DsdFetcher(requests)
    return DatasetsReader(tree, dsd_fetcher=dsd_fetcher)


class XmlNode(object):
    def __init__(self, node):
        self._node = node
        
    def map_nodes(self, path, func):
        return map(func, self.findall(path))
    
    def find(self, path):
        return XmlNode(self._node.find(path))
    
    def findall(self, path):
        return map(XmlNode, self._node.findall(path))
    
    def get(self, name):
        return self._node.get(name)
    
    def inner_text(self):
        return inner_text(self._node)


class GenericElementTypes(object):
    def _expand(name):
        return "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}" + name
    
    DataSet = _expand("DataSet")
    Series = _expand("Series")
    SeriesKey = _expand("SeriesKey")
    KeyFamilyRef = _expand("KeyFamilyRef")
    Obs = _expand("Obs")
    Value = _expand("Value")
    Time = _expand("Time")
    ObsValue = _expand("ObsValue")


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
        

class DatasetsReader(object):
    def __init__(self, tree, dsd_fetcher):
        self._tree = tree
        self._dsd_fetcher = dsd_fetcher
    
    def datasets(self):
        return self._tree.map_nodes(GenericElementTypes.DataSet, self._read_dataset_element)
        
    def _read_dataset_element(self, element):
        return DatasetReader(element, self._dsd_fetcher)

class DatasetReader(object):
    def __init__(self, element, dsd_fetcher):
        self._element = element
        self._dsd_fetcher = dsd_fetcher
    
    def key_family(self):
        key_family_ref_element = self._element.find(GenericElementTypes.KeyFamilyRef)
        ref = key_family_ref_element.inner_text().strip()
        dsd_reader = self._dsd_reader()
        key_families = dict(
            (key_family.id, key_family)
            for key_family in dsd_reader.key_families()
        )
        return KeyFamily(
            key_families[ref],
            self._dsd_reader(),
        )
    
    def series(self):
        key_family = self.key_family()
        return self._element.map_nodes(
            GenericElementTypes.Series, 
            lambda element: self._read_series_element(key_family, element)
        )
        
    def _dsd_reader(self):
        key_family_uri = self._element.get("keyFamilyURI")
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
    
    def describe_value(self, concept_ref, code_value, lang):
        dimension = self._find_dimension(concept_ref)
        concept = self._dsd_reader.concept(concept_ref)
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
        key_value_path = "/".join([
            GenericElementTypes.SeriesKey,
            GenericElementTypes.Value,
        ])
        key_value_elements = self._element.findall(key_value_path)
        
        return OrderedDict(
            self._key_family.describe_value(element.get("concept"), element.get("value"), lang=lang)
            for element in key_value_elements
        )
    
    def observations(self):
        return self._element.map_nodes(
            GenericElementTypes.Obs,
            self._read_obs_element,
        )
    
    def _read_obs_element(self, obs_element):
        time_element = obs_element.find(GenericElementTypes.Time)
        value_element = obs_element.find(GenericElementTypes.ObsValue)
        return Observation(time_element.inner_text(), value_element.get("value"))


class Observation(object):
    def __init__(self, time, value):
        self.time = time
        self.value = value
