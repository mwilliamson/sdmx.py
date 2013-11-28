import io

from nose.tools import istest, assert_equal

import sdmx


@istest
def concepts_are_detected_when_contained_in_concept_scheme():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
<Concepts>
<structure:ConceptScheme>
<structure:Concept id="itm_newa">
<structure:Name xml:lang="en">List of products - EAA</structure:Name>
</structure:Concept>
</structure:ConceptScheme>
</Concepts>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    concept, = dsd_reader.concepts()
    assert_equal("itm_newa", concept.id)


@istest
def concepts_are_detected_when_contained_directly_in_concepts_element():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <Concepts>
        <structure:Concept id="itm_newa">
            <structure:Name xml:lang="en">List of products - EAA</structure:Name>
        </structure:Concept>
    </Concepts>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    concept, = dsd_reader.concepts()
    assert_equal("itm_newa", concept.id)


@istest
def concepts_are_indexed_by_id():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <Concepts>
        <structure:Concept id="itm_newa">
            <structure:Name xml:lang="en">List of products - EAA</structure:Name>
        </structure:Concept>
    </Concepts>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    assert_equal("itm_newa", dsd_reader.concept("itm_newa").id)
    assert_equal(None, dsd_reader.concept("itm_newb"))


@istest
def concept_names_are_read_by_language():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
<Concepts>
<structure:ConceptScheme>
<structure:Concept id="itm_newa"><structure:Name xml:lang="en">List of products - EAA</structure:Name>
<structure:Name xml:lang="de">Liste der Produkte - LGR</structure:Name>
<structure:Name xml:lang="fr">Liste de produits - EAA</structure:Name>
</structure:Concept>
</structure:ConceptScheme>
</Concepts>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    concept, = dsd_reader.concepts()
    assert_equal("List of products - EAA", concept.name("en"))


@istest
def code_lists_are_read_with_ids_and_names():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <CodeLists>
        <structure:CodeList id="CL_ITM_NEWA" agencyID="EUROSTAT" isFinal="true">
            <structure:Name xml:lang="en">List of products - EAA</structure:Name>
            <structure:Name xml:lang="de">Liste der Produkte - LGR</structure:Name>
        </structure:CodeList>
    </CodeLists>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    code_list, = dsd_reader.code_lists()
    assert_equal("CL_ITM_NEWA", code_list.id)
    assert_equal("List of products - EAA", code_list.name(lang="en"))
    assert_equal("Liste der Produkte - LGR", code_list.name(lang="de"))


@istest
def code_lists_are_indexed_by_id():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <CodeLists>
        <structure:CodeList id="CL_ITM_NEWA" agencyID="EUROSTAT" isFinal="true">
        </structure:CodeList>
    </CodeLists>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    assert_equal("CL_ITM_NEWA", dsd_reader.code_list("CL_ITM_NEWA").id)
    assert_equal(None, dsd_reader.code_list("CL_ITM_NEWB"))


@istest
def codes_can_be_read_from_code_lists():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <CodeLists>
        <structure:CodeList id="CL_ITM_NEWA" agencyID="EUROSTAT" isFinal="true">
            <structure:Code value="40000">
                <structure:Description xml:lang="en">Total labour force input</structure:Description>
                <structure:Description xml:lang="de">Landwirtschaftlicher Arbeitseinsatz insgesamt</structure:Description>
            </structure:Code>
        </structure:CodeList>
    </CodeLists>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    code_list, = dsd_reader.code_lists()
    code, = code_list.codes()
    
    assert_equal("40000", code.value)
    assert_equal(None, code.parent_code_id())
    assert_equal("Total labour force input", code.description("en"))
    assert_equal("Landwirtschaftlicher Arbeitseinsatz insgesamt", code.description("de"))


@istest
def codes_can_have_parents():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <CodeLists>
        <structure:CodeList id="CL_ITM_NEWA" agencyID="EUROSTAT" isFinal="true">
            <structure:Code value="40000" parentCode="41000" />
        </structure:CodeList>
    </CodeLists>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    code_list, = dsd_reader.code_lists()
    code, = code_list.codes()
    
    assert_equal("41000", code.parent_code_id())


@istest
def codes_are_indexed_by_value():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <CodeLists>
        <structure:CodeList id="CL_ITM_NEWA" agencyID="EUROSTAT" isFinal="true">
            <structure:Code value="40000">
            </structure:Code>
        </structure:CodeList>
    </CodeLists>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    code_list, = dsd_reader.code_lists()
    
    assert_equal("40000", code_list.code("40000").value)
    assert_equal(None, code_list.code("40001"))


@istest
def key_families_are_read_with_id_and_name():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <KeyFamilies>
        <structure:KeyFamily id="MON20123_2" agencyID="OECD">
            <structure:Name xml:lang="en">2012 F) OECD countries : Consumer Support Estimate by country</structure:Name>
            <structure:Name xml:lang="fr">2012 F) OCDE : Estimation du soutien aux consommateurs par pays</structure:Name>
        </structure:KeyFamily>
    </KeyFamilies>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    key_family, = dsd_reader.key_families()
    
    assert_equal("MON20123_2", key_family.id)
    assert_equal("2012 F) OECD countries : Consumer Support Estimate by country", key_family.name("en"))
    assert_equal("2012 F) OCDE : Estimation du soutien aux consommateurs par pays", key_family.name("fr"))


@istest
def key_family_dimensions_have_concept_and_code_list():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <Concepts>
        <structure:Concept id="COUNTRY" agencyID="OECD">
            <structure:Name xml:lang="en">Country</structure:Name>
        </structure:Concept>
    </Concepts>
    <CodeList>
        <structure:CodeList id="CL_MON20123_2_COUNTRY" agencyID="OECD">
            <structure:Name xml:lang="en">MON20123_2_COUNTRY codelist</structure:Name>
        </structure:CodeList>
    </CodeList>
    <KeyFamilies>
        <structure:KeyFamily id="MON20123_2" agencyID="OECD">
            <structure:Name xml:lang="en">2012 F) OECD countries : Consumer Support Estimate by country</structure:Name>
            <structure:Components>
                <structure:Dimension conceptRef="COUNTRY" codelist="CL_MON20123_2_COUNTRY"/>
            </structure:Components>
        </structure:KeyFamily>
    </KeyFamilies>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    key_family, = dsd_reader.key_families()
    dimension, = key_family.dimensions()
    
    assert_equal("COUNTRY", dimension.concept_ref())
    assert_equal("CL_MON20123_2_COUNTRY", dimension.code_list_id())
    #~ assert_equal("Country", dimension.concept().name(lang="en"))
    #~ assert_equal("MON20123_2_COUNTRY codelist", dimension.code_list().name(lang="en"))



@istest
def time_dimension_can_be_read_from_key_family():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <KeyFamilies>
        <structure:KeyFamily id="MON20123_2" agencyID="OECD">
            <structure:Name xml:lang="en">2012 F) OECD countries : Consumer Support Estimate by country</structure:Name>
            <structure:Components>
                <structure:TimeDimension conceptRef="TIME" codelist="CL_MON2012TSE_O_TIME" />
            </structure:Components>
        </structure:KeyFamily>
    </KeyFamilies>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    key_family, = dsd_reader.key_families()
    dimension = key_family.time_dimension()
    
    assert_equal("TIME", dimension.concept_ref())
    assert_equal("CL_MON2012TSE_O_TIME", dimension.code_list_id())



@istest
def primary_measure_can_be_read_from_key_family():
    dsd_file = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <KeyFamilies>
        <structure:KeyFamily id="MON20123_2" agencyID="OECD">
            <structure:Name xml:lang="en">2012 F) OECD countries : Consumer Support Estimate by country</structure:Name>
            <structure:Components>
                <structure:PrimaryMeasure conceptRef="OBS_VALUE"><TextFormat textType="Double" /></structure:PrimaryMeasure>
            </structure:Components>
        </structure:KeyFamily>
    </KeyFamilies>
</Structure>""")
    
    dsd_reader = sdmx.dsd_reader(fileobj=dsd_file)
    key_family, = dsd_reader.key_families()
    dimension = key_family.primary_measure()
    
    assert_equal("OBS_VALUE", dimension.concept_ref())
