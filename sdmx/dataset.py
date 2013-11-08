import io
import collections

from xml.etree.cElementTree import parse as _parse_xml

from .xmlcommon import inner_text
from . import dsd


def reader(fileobj, requests=None):
    tree = _parse_xml(fileobj)
    dsd_fetcher = DsdFetcher(requests)
    return DatasetsReader(tree, dsd_fetcher=dsd_fetcher)


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
        path = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}DataSet"
        elements = self._tree.findall(path)
        return map(self._read_dataset_element, elements)
        
    def _read_dataset_element(self, element):
        return DatasetReader(element, self._dsd_fetcher)

class DatasetReader(object):
    def __init__(self, element, dsd_fetcher):
        self._element = element
        self._dsd_fetcher = dsd_fetcher
    
    def key_family(self):
        key_family_ref_path = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}KeyFamilyRef"
        key_family_ref_element = self._element.find(key_family_ref_path)
        ref = inner_text(key_family_ref_element).strip()
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
        path = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Series"
        elements = self._element.findall(path)
        key_family = self.key_family()
        return [
            self._read_series_element(key_family, element)
            for element in elements
        ]
        
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
            "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}SeriesKey",
            "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Value",
        ])
        key_value_elements = self._element.findall(key_value_path)
        
        return collections.OrderedDict(
            self._key_family.describe_value(element.get("concept"), element.get("value"), lang=lang)
            for element in key_value_elements
        )
    
    def observations(self):
        obs_path = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Obs"
        obs_elements = self._element.findall(obs_path)
        return map(self._read_obs_element, obs_elements)
    
    def _read_obs_element(self, obs_element):
        time_element = obs_element.find("{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}Time")
        value_element = obs_element.find("{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}ObsValue")
        return Observation(inner_text(time_element), value_element.get("value"))


class Observation(object):
    def __init__(self, time, value):
        self.time = time
        self.value = value
