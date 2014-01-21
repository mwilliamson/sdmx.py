from .xmlcommon import inner_text, parse_xml


def reader(fileobj):
    tree = parse_xml(fileobj)
    return DsdReader(tree)
    

class DsdReader(object):
    _concept_path = "//".join([
        "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}Concepts",
        "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Concept",
    ])
    
    _code_list_path = "/".join([
        "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}CodeLists",
        "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}CodeList",
    ])
    
    def __init__(self, tree):
        self._tree = tree
    
    def concepts(self):
        concept_elements = self._tree.findall(self._concept_path)
        return map(self._read_concept_element, concept_elements)
    
    def concept(self, id):
        path = "{0}[@id='{1}']".format(self._concept_path, id)
        element = self._tree.find(path)
        if element is None:
            return element
        else:
            return self._read_concept_element(element)
    
    def _read_concept_element(self, concept_element):
        return ConceptReader(concept_element.get("id"), concept_element)
    
    def code_lists(self):
        elements = self._tree.findall(self._code_list_path)
        return map(self._read_code_list_element, elements)
    
    def code_list(self, id):
        path = "{0}[@id='{1}']".format(self._code_list_path, id)
        element = self._tree.find(path)
        if element is None:
            return None
        else:
            return self._read_code_list_element(element)
    
    def _read_code_list_element(self, element):
        return CodeListReader(element.get("id"), element)

    def key_families(self):
        path = [
            "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}KeyFamilies",
            "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}KeyFamily",
        ]
        elements = self._tree.findall("/".join(path))
        return map(self._read_key_family_element, elements)
    
    def _read_key_family_element(self, element):
        return KeyFamilyReader(element.get("id"), element)
        

class ConceptReader(object):
    def __init__(self, id, element):
        self.id = id
        self._element = element

    def name(self, lang):
        return _read_name(self._element, lang=lang)


class CodeListReader(object):
    _code_path = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Code"
    
    def __init__(self, id, element):
        self.id = id
        self._element = element
    
    def name(self, lang):
        return _read_name(self._element, lang=lang)
        
    def codes(self):
        elements = self._element.findall(self._code_path)
        return map(self._read_code_element, elements)
    
    def code(self, value):
        path = "{0}[@value='{1}']".format(self._code_path, value)
        element = self._element.find(path)
        if element is None:
            return None
        else:
            return self._read_code_element(element)
    
    def _read_code_element(self, element):
        return CodeReader(element.get("value"), element)

        
class CodeReader(object):
    def __init__(self, value, element):
        self.value = value
        self._element = element

    def description(self, lang):
        return _read_description(self._element, lang=lang)
        
    def parent_code_id(self):
        return self._element.get("parentCode") or None


class KeyFamilyReader(object):
    def __init__(self, id, element):
        self.id = id
        self._element = element
    
    def name(self, lang):
        return _read_name(self._element, lang=lang)
    
    def dimensions(self):
        path = self._dimension_path("Dimension")
        elements = self._element.findall(path)
        return map(self._read_dimension_element, elements)

    def time_dimension(self):
        path = self._dimension_path("TimeDimension")
        element = self._element.find(path)
        return self._read_dimension_element(element)
        
    def primary_measure(self):
        path = self._dimension_path("PrimaryMeasure")
        element = self._element.find(path)
        return self._read_dimension_element(element)
    
    def _dimension_path(self, name):
        return "/".join([
            "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Components",
            "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}" + name,
        ])

    def _read_dimension_element(self, element):
        return KeyFamilyDimensionReader(element)


class KeyFamilyDimensionReader(object):
    def __init__(self, element):
        self._element = element
    
    def concept_ref(self):
        return self._element.get("conceptRef")
    
    def code_list_id(self):
        return self._element.get("codelist")


def _read_name(element, lang):
    tag_name = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Name"
    return _read_element_of_lang(element, tag_name, lang)


def _read_description(element, lang):
    tag_name = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure}Description"
    return _read_element_of_lang(element, tag_name, lang)


def _read_element_of_lang(element, path, lang):
    path_with_lang = "%s[@{http://www.w3.org/XML/1998/namespace}lang='%s']" % (path, lang)
    return inner_text(element.find(path_with_lang)).strip()
    
