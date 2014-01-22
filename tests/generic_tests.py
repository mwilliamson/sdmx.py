import io

from nose.tools import istest, nottest, assert_equal
import funk

import sdmx
from . import testing


@nottest
class GenericDataTests(object):
    @istest
    def dataset_key_family_is_retrieved_from_dsd(self):
        dataset_file = io.BytesIO(
        b"""<message:MessageGroup xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common" xsi:schemaLocation="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic http://www.sdmx.org/docs/2_0/SDMXGenericData.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message http://www.sdmx.org/docs/2_0/SDMXMessage.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message">
        <DataSet keyFamilyURI="http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true">
            <KeyFamilyRef>MON2012TSE_O</KeyFamilyRef>
        </DataSet>
    </message:MessageGroup>""")
        dataset_reader = self._reader(dataset_file)
        dataset = next(dataset_reader.datasets())
        
        assert_equal("2012 A) OECD: Estimate of support to agriculture", dataset.key_family().name("en"))
        assert_equal(["Country", "Indicator"], dataset.key_family().describe_dimensions("en"))


    @istest
    def data_can_be_stored_in_generic_data_element(self):
        dataset_file = io.BytesIO(
        b"""<message:genericData xmlns:message="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message" xmlns:generic="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic" xmlns:common="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common">
        <message:DataSet keyFamilyURI="http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true">
            <generic:KeyFamilyRef>MON2012TSE_O</generic:KeyFamilyRef>
        </message:DataSet>
    </message:genericData>""")
        dataset_reader = self._reader(dataset_file)
        dataset = next(dataset_reader.datasets())
        
        assert_equal("2012 A) OECD: Estimate of support to agriculture", dataset.key_family().name("en"))
        assert_equal(["Country", "Indicator"], dataset.key_family().describe_dimensions("en"))


    @istest
    def series_key_is_read_using_dsd_concepts_and_code_lists(self):
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
        dataset_reader = self._reader(dataset_file)
        dataset = next(dataset_reader.datasets())
        series = next(dataset.series())
        
        assert_equal(
            [("Country", ["OECD(EUR million)"]), ("Indicator", ["Total value of production (at farm gate)"])],
            list(series.describe_key(lang="en").items()),
        )


    @istest
    def key_description_includes_description_of_parent_concepts(self):
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
        dataset_reader = self._reader(dataset_file)
        dataset = next(dataset_reader.datasets())
        series = next(dataset.series())
        
        assert_equal(
            [
                ("Country", ["OECD(EUR million)"]),
                ("Indicator", ["Total value of production (at farm gate)", "of which: share of MPS commodities, percentage"])
            ],
            list(series.describe_key(lang="en").items()),
        )


    @istest
    def observations_have_time_and_value(self):
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
        dataset_reader = self._reader(dataset_file)
        dataset = next(dataset_reader.datasets())
        series = next(dataset.series())
        observations = iter(series.observations())
        first_obs = next(observations)
        second_obs = next(observations)
        
        assert_equal("1986", first_obs.time)
        assert_equal("538954.220075479", first_obs.value)
        
        assert_equal("1987", second_obs.time)
        assert_equal("598184.668422966", second_obs.value)


    #~ @istest
    def time_is_read_from_code_list_if_time_dimension_has_code_dimension(self):
        with testing.open("time-code-list.sdmx.xml", "rb") as dataset_file:
            with testing.open("time-code-list.dsd.xml", "rb") as dsd_file:
                dataset_reader = self._message_reader(dataset_file, dsd_fileobj=dsd_file)
                dataset, = dataset_reader.datasets()
                series, = dataset.series()
                first_obs, second_obs = series.observations(lang="en")
                
                assert_equal("1986", first_obs.time)
                assert_equal("1987", second_obs.time)


    #~ @istest
    def whitespace_is_stripped_before_looking_up_time_code(self):
        with testing.open("time-code-list-whitespace.sdmx.xml", "rb") as dataset_file:
            with testing.open("time-code-list.dsd.xml", "rb") as dsd_file:
                dataset_reader = self._message_reader(dataset_file, dsd_fileobj=dsd_file)
                dataset, = dataset_reader.datasets()
                series, = dataset.series()
                first_obs, second_obs = series.observations(lang="en")
                
                assert_equal("1986", first_obs.time)
                assert_equal("1987", second_obs.time)


    #~ @istest
    def value_error_is_raised_if_observation_time_uses_code_and_language_is_not_specified(self):
        with testing.open("time-code-list.sdmx.xml", "rb") as dataset_file:
            with testing.open("time-code-list.dsd.xml", "rb") as dsd_file:
                dataset_reader = self._message_reader(dataset_file, dsd_fileobj=dsd_file)
                dataset, = dataset_reader.datasets()
                series, = dataset.series()
                try:
                    series.observations()
                    assert False, "Expected ValueError"
                except ValueError as error:
                    assert_equal("Observation time uses code list, but language is not specified", str(error))


    #~ @istest
    def key_values_can_be_read_from_group(self):
        with testing.open("groups.sdmx.xml", "rb") as dataset_file:
            with testing.open("groups.dsd.xml", "rb") as dsd_file:
                dataset_reader = self._message_reader(dataset_file, dsd_fileobj=dsd_file)
                dataset, = dataset_reader.datasets()
                series, = dataset.series()
                
                assert_equal(
                    [
                        ("Indicator", ["Total value of production (at farm gate)", "of which: share of MPS commodities, percentage"]),
                        ("Country", ["OECD(EUR million)"]),
                    ],
                    list(series.describe_key(lang="en").items()),
                )

    def _reader(self, dataset_file):
        context = funk.Context()
        requests = context.mock()
        response = context.mock()
        funk.allows(requests).get("http://stats.oecd.org/RestSDMX/sdmx.ashx/GetKeyFamily/MON2012TSE_O/OECD/?resolveRef=true").returns(response)
        funk.allows(response).iter_content(16 * 1024).returns(_dsd_chunks())
        
        return self._message_reader(fileobj=dataset_file, requests=requests)
    
    def _message_reader(self, *args, **kwargs):
        return sdmx.generic_data_message_reader(*args, lazy=self.lazy, **kwargs)

@istest
class EagerGenericTests(GenericDataTests):
    lazy = False


@istest
class LazyGenericTests(GenericDataTests):
    lazy = True


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
                <structure:TimeDimension conceptRef="TIME" />
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
