import functools
from xml.dom import pulldom

from .dataset import data_message_reader, Observation
from . import xmlpull


class MessageElementTypes(object):
    def _expand(name):
        return "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}" + name
    
    DataSet = _expand("DataSet")


class GenericElementTypes(object):
    def _expand(name):
        return "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic}" + name
    
    DataSet = _expand("DataSet")
    Group = _expand("Group")
    GroupKey = _expand("GroupKey")
    Series = _expand("Series")
    SeriesKey = _expand("SeriesKey")
    KeyFamilyRef = _expand("KeyFamilyRef")
    Obs = _expand("Obs")
    Value = _expand("Value")
    Time = _expand("Time")
    ObsValue = _expand("ObsValue")


class GenericDataMessageParser(object):
    def seek_dataset_node(self, event_stream):
        while True:
            event, node = next(event_stream)
            # TODO: check namespace
            if event == pulldom.START_ELEMENT and node.localName == "DataSet":
                return node
        
    def key_family_for_dataset(self, event_stream, dataset_node, dsd_reader):
        event, node = event_stream.seek(pulldom.START_ELEMENT, [pulldom.CHARACTERS])
        # TODO: check namespace
        assert node.localName == "KeyFamilyRef"
        ref = event_stream.inner_text().strip()
        key_families = dict(
            (key_family.id, key_family)
            for key_family in dsd_reader.key_families()
        )
        return key_families[ref]
        
    def seek_series_node(self, event_stream):
        while True:
            event, node = next(event_stream)
            # TODO: check namespace
            if event == pulldom.START_ELEMENT and node.localName == "Series":
                series_key = self._read_series_key(event_stream)
                return node, series_key
    
    def _read_series_key(self, event_stream):
        self._seek_series_key(event_stream)
        key = []
        while True:
            event, node = next(event_stream)
            if event == pulldom.START_ELEMENT and node.localName == "Value":
                key.append((node.getAttribute("concept"), node.getAttribute("value")))
            elif event == pulldom.END_ELEMENT and node.localName == "SeriesKey":
                return key
    
    def _seek_series_key(self, event_stream):
        while True:
            event, node = next(event_stream)
            # TODO: check namespace
            if event == pulldom.START_ELEMENT and node.localName == "SeriesKey":
                return node
        
    
    def _get_series_elements_generator(self, dataset_element):
        for child in dataset_element.children():
            name = child.qualified_name()
            if name == GenericElementTypes.Group:
                group_key = self._group_key(child)
                for series_element in child.findall(GenericElementTypes.Series):
                    series_key = group_key + self._series_key(series_element)
                    yield series_element, series_key
            
            elif name == GenericElementTypes.Series:
                yield child, self._series_key(child)
        
    def _group_key(self, group_element):
        key_element = group_element.find(GenericElementTypes.GroupKey)
        return self._read_key_element(key_element)
        
    def _series_key(self, series_element):
        key_element = series_element.find(GenericElementTypes.SeriesKey)
        return self._read_key_element(key_element)
        
    def read_observations(self, key_family, series_element):
        return series_element.map_nodes(
            GenericElementTypes.Obs,
            self._read_obs_element,
        )
        
    def _read_key_element(self, key_element):
        key_value_elements = key_element.findall(GenericElementTypes.Value)
        
        return [
            (element.get("concept"), element.get("value"))
            for element in key_value_elements
        ]
        
    def _read_obs_element(self, obs_element):
        time_element = obs_element.find(GenericElementTypes.Time)
        value_element = obs_element.find(GenericElementTypes.ObsValue)
        return Observation(time_element.inner_text(), value_element.get("value"))


generic_data_message_reader = functools.partial(data_message_reader, GenericDataMessageParser())
