import functools

from .dataset import data_message_reader, Observation


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


class GenericDataMessageParser(object):
    def get_dataset_elements(self, message_element):
        return message_element.findall(GenericElementTypes.DataSet)
        
    def key_family_for_dataset(self, dataset_element, dsd_reader):
        key_family_ref_element = dataset_element.find(GenericElementTypes.KeyFamilyRef)
        ref = key_family_ref_element.inner_text().strip()
        key_families = dict(
            (key_family.id, key_family)
            for key_family in dsd_reader.key_families()
        )
        return key_families[ref]
    
    def get_series_elements(self, dataset_element):
        return dataset_element.findall(GenericElementTypes.Series)
        
    def series_key(self, series_element):
        key_value_path = "/".join([
            GenericElementTypes.SeriesKey,
            GenericElementTypes.Value,
        ])
        key_value_elements = series_element.findall(key_value_path)
        
        return (
            (element.get("concept"), element.get("value"))
            for element in key_value_elements
        )
        
    def read_observations(self, key_family, series_element):
        return series_element.map_nodes(
            GenericElementTypes.Obs,
            self._read_obs_element,
        )
        
    def _read_obs_element(self, obs_element):
        time_element = obs_element.find(GenericElementTypes.Time)
        value_element = obs_element.find(GenericElementTypes.ObsValue)
        return Observation(time_element.inner_text(), value_element.get("value"))


generic_data_message_reader = functools.partial(data_message_reader, GenericDataMessageParser())
