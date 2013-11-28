import io
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from .xmlcommon import parse_xml, XmlNode
from . import dsd
from .dataset import data_message_reader, Observation


def compact_data_message_reader(fileobj, requests=None):
    return data_message_reader(CompactDataMessageParser(), fileobj, requests=requests)


class CompactDataMessageParser(object):
    def get_dataset_elements(self, message_element):
        return _children_with_local_name(message_element, "DataSet")
        
    def key_family_for_dataset(self, dataset_element, dsd_reader):
        # Assume a single key family
        key_family, = dsd_reader.key_families()
        return key_family
    
    def get_series_elements(self, dataset_element):
        return _children_with_local_name(dataset_element, "Series")
        
    def series_key(self, series_element):
        return series_element.attributes()
        
    def read_observations(self, series_element):
        return map(
            self._read_obs_element,
            _children_with_local_name(series_element, "Obs"),
        )
        
    def _read_obs_element(self, obs_element):
        # TODO: read appropriate attribute names from key family
        time = obs_element.get("TIME")
        value = obs_element.get("OBS_VALUE")
        return Observation(time, value)


def _children_with_local_name( parent, local_name):
    # Ignore the namespace since it's dataset dependent
    # The alternative is to use the SDMX converter to convert to a Generic
    # Data Message, but the source code appears to indicate they also ignore
    # namespace
    for element in parent.children():
        if element.local_name() == local_name:
            yield element
        
        
