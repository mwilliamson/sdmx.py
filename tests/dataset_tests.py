import io

from nose.tools import istest, assert_equal
import funk

import sdmx


@istest
def dataset_key_family_is_retrieved_from_dsd():
    dataset_file = io.BytesIO(
    b"""<message:MessageGroup xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common" xsi:schemaLocation="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic http://www.sdmx.org/docs/2_0/SDMXGenericData.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message http://www.sdmx.org/docs/2_0/SDMXMessage.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message">
    <DataSet keyFamilyURI="http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true">
        <KeyFamilyRef>MON2012TSE_O</KeyFamilyRef>
    </DataSet>
</message:MessageGroup>""")
    dataset_reader = _reader(dataset_file)
    dataset, = dataset_reader.datasets()
    
    assert_equal("2012 A) OECD: Estimate of support to agriculture", dataset.key_family().name("en"))
    assert_equal(["Country", "Indicator"], dataset.key_family().describe_dimensions("en"))


@istest
def series_key_is_read_using_dsd_concepts_and_code_lists():
    dataset_file = io.BytesIO(
    b"""<message:MessageGroup xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common" xsi:schemaLocation="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic http://www.sdmx.org/docs/2_0/SDMXGenericData.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message http://www.sdmx.org/docs/2_0/SDMXMessage.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message">
    <DataSet keyFamilyURI="http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true">
        <KeyFamilyRef>MON2012TSE_O</KeyFamilyRef>
        <Series>
            <SeriesKey>
                <Value concept="COUNTRY" value="OECD-E" />
                <Value concept="INDIC" value="TO-VP" />
            </SeriesKey>
        </Series>
    </DataSet>
</message:MessageGroup>""")
    dataset_reader = _reader(dataset_file)
    dataset, = dataset_reader.datasets()
    series, = dataset.series()
    
    assert_equal(
        [("Country", ["OECD(EUR million)"]), ("Indicator", ["Total value of production (at farm gate)"])],
        list(series.describe_key(lang="en").items()),
    )


@istest
def key_description_includes_description_of_parent_concepts():
    dataset_file = io.BytesIO(
    b"""<message:MessageGroup xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common" xsi:schemaLocation="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic http://www.sdmx.org/docs/2_0/SDMXGenericData.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message http://www.sdmx.org/docs/2_0/SDMXMessage.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message">
    <DataSet keyFamilyURI="http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true">
        <KeyFamilyRef>MON2012TSE_O</KeyFamilyRef>
        <Series>
            <SeriesKey>
                <Value concept="COUNTRY" value="OECD-E" />
                <Value concept="INDIC" value="TO-VP1P" />
            </SeriesKey>
        </Series>
    </DataSet>
</message:MessageGroup>""")
    dataset_reader = _reader(dataset_file)
    dataset, = dataset_reader.datasets()
    series, = dataset.series()
    
    assert_equal(
        [
            ("Country", ["OECD(EUR million)"]),
            ("Indicator", ["Total value of production (at farm gate)", "of which: share of MPS commodities, percentage"])
        ],
        list(series.describe_key(lang="en").items()),
    )


@istest
def observations_have_time_and_value():
    dataset_file = io.BytesIO(
    b"""<message:MessageGroup xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common" xsi:schemaLocation="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic http://www.sdmx.org/docs/2_0/SDMXGenericData.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message http://www.sdmx.org/docs/2_0/SDMXMessage.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message">
    <DataSet keyFamilyURI="http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true">
        <KeyFamilyRef>MON2012TSE_O</KeyFamilyRef>
        <Series>
            <SeriesKey>
                <Value concept="COUNTRY" value="OECD-E" />
                <Value concept="INDIC" value="TO-VP" />
            </SeriesKey>
            <Obs><Time>1986</Time><ObsValue value="538954.220075479"/></Obs>
            <Obs><Time>1987</Time><ObsValue value="598184.668422966"/></Obs>
        </Series>
    </DataSet>
</message:MessageGroup>""")
    dataset_reader = _reader(dataset_file)
    dataset, = dataset_reader.datasets()
    series, = dataset.series()
    first_obs, second_obs = series.observations()
    
    assert_equal("1986", first_obs.time)
    assert_equal("538954.220075479", first_obs.value)
    
    assert_equal("1987", second_obs.time)
    assert_equal("598184.668422966", second_obs.value)


def _reader(dataset_file):
    context = funk.Context()
    requests = context.mock()
    response = context.mock()
    funk.allows(requests).get("http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true").returns(response)
    funk.allows(response).iter_content(16 * 1024).returns(_dsd_chunks())
    
    return sdmx.dataset_reader(fileobj=dataset_file, requests=requests)

def _dsd_chunks():
    fileobj = io.BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<Structure xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:structure="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure">
    <CodeLists>
        <structure:CodeList id="CL_MON2012TSE_O_COUNTRY" agencyID="OECD">
            <structure:Code value="OECD-E">
                <structure:Description xml:lang="en">OECD(EUR million)</structure:Description>
            </structure:Code>
        </structure:CodeList>
        <structure:CodeList id="CL_MON2012TSE_O_INDIC" agencyID="OECD">
            <structure:Code value="TO-VP">
                <structure:Description xml:lang="en">Total value of production (at farm gate)</structure:Description>
            </structure:Code>
            <structure:Code value="TO-VP1P" parentCode="TO-VP">
                <structure:Description xml:lang="en">of which: share of MPS commodities, percentage</structure:Description>
            </structure:Code>
        </structure:CodeList>
    </CodeLists>
    <Concepts>
        <structure:Concept id="COUNTRY">
            <structure:Name xml:lang="en">Country</structure:Name>
        </structure:Concept>
        <structure:Concept id="INDIC">
            <structure:Name xml:lang="en">Indicator</structure:Name>
        </structure:Concept>
    </Concepts>
    <KeyFamilies>
        <structure:KeyFamily id="MON2012TSE_O" agencyID="OECD">
            <structure:Name xml:lang="en">2012 A) OECD: Estimate of support to agriculture</structure:Name>
            <structure:Components>
                <structure:Dimension conceptRef="COUNTRY" codelist="CL_MON2012TSE_O_COUNTRY"/>
                <structure:Dimension conceptRef="INDIC" codelist="CL_MON2012TSE_O_INDIC"/>
            </structure:Components>
        </structure:KeyFamily>
    </KeyFamilies>
</Structure>""")
    
    buf = []
    while True:
        buf = fileobj.read(16 * 1024)
        if buf:
            yield buf
        else:
            return
