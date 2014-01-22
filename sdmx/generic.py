import functools
from xml.dom import pulldom

from .dataset import data_message_reader, Observation


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


def _seek_event_stream(stream, desired_event, ignore):
    while True:
        event, node = next(stream)
        if event == desired_event:
            return event, node
        elif not event in ignore:
            raise ValueError("Event {0} before desired event {1}".format(event, desired_event))

def _read_inner_text(stream):
    text = []
    level = 1
    while level > 0:
        event, node = next(stream)
        if event == pulldom.START_ELEMENT:
            level += 1
        elif event == pulldom.END_ELEMENT:
            level -= 1
        elif event == pulldom.CHARACTERS:
            text.append(node.nodeValue)
    
    return "".join(text)


class GenericDataMessageParser(object):
    def is_dataset_element(self, element):
        # TODO: check namespace
        return element.localName == "DataSet"
        
    def key_family_for_dataset(self, event_stream, dataset_node, dsd_reader):
        event, node = _seek_event_stream(event_stream, pulldom.START_ELEMENT, [pulldom.CHARACTERS])
        # TODO: check namespace
        assert node.localName == "KeyFamilyRef"
        ref = _read_inner_text(event_stream).strip()
        key_families = dict(
            (key_family.id, key_family)
            for key_family in dsd_reader.key_families()
        )
        return key_families[ref]
    
    def get_series_elements(self, dataset_element):
        return list(self._get_series_elements_generator(dataset_element))
    
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
