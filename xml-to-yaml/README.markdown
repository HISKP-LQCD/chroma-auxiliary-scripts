# XML to YAML

Converts Chroma XML files to [YAML](http://yaml.org/) and back again.

## Usage

XML → YAML:

    xml_to_yaml.py XML_FILE YAML_FILE

YAML → XML

    yaml_to_xml.py YAML_FILE XML_FILE

## Example

Chroma uses a subset of XML for its input and output files. There are just tags
(`<elem>`), there are no attributes (`key="value"`). The head of an input file
might look like this:

```xml
<?xml version="1.0"?>
<Params>
  <MCControl>
    <Cfg>
      <cfg_type>DISORDERED</cfg_type>
      <cfg_file>DUMMY</cfg_file>
    </Cfg>

    <RNG>
      <Seed>
        <elem>11</elem>
        <elem>0 </elem>
        <elem>0 </elem>
        <elem>0 </elem>
      </Seed>
    </RNG>

    <StartUpdateNum>0</StartUpdateNum>
    <NWarmUpUpdates>0</NWarmUpUpdates>
    <NProductionUpdates>100</NProductionUpdates>
    <NUpdatesThisRun>100</NUpdatesThisRun>
    <SaveInterval>1</SaveInterval>

    <SavePrefix>wilson-clover</SavePrefix>
    <SaveVolfmt>SINGLEFILE</SaveVolfmt>
    <InlineMeasurements>
      <elem>
        <Name>POLYAKOV_LOOP</Name>
        <Frequency>1</Frequency>
        <Param>
          <version>2</version>
        </Param>
        <NamedObject>
          <gauge_id>default_gauge_field</gauge_id>
        </NamedObject>
      </elem>
    </InlineMeasurements>
  </MCControl>

  <HMCTrj>
    <Monomials>
      <elem>
        <Name>GAUGE_MONOMIAL</Name>
```

Every tag has its tag-name and a list of children. The leaves of the tree are
just text nodes. This data structure can be represented as a dict (that is the
name in Python, Perl calls those “hash”, C++ “map”) that contains a list of
child elements.

That structure can be persisted into YAML, which then looks like this:

```yml
Params:
- MCControl:
  - Cfg:
    - cfg_type: DISORDERED
    - cfg_file: DUMMY
  - RNG:
    - Seed:
      - elem: '11'
      - elem: '0 '
      - elem: '0 '
      - elem: '0 '
  - StartUpdateNum: '0'
  - NWarmUpUpdates: '0'
  - NProductionUpdates: '100'
  - NUpdatesThisRun: '100'
  - SaveInterval: '1'
  - SavePrefix: wilson-clover
  - SaveVolfmt: SINGLEFILE
  - InlineMeasurements:
    - elem:
      - Name: POLYAKOV_LOOP
      - Frequency: '1'
      - Param:
        - version: '2'
      - NamedObject:
        - gauge_id: default_gauge_field
- HMCTrj:
  - Monomials:
    - elem:
      - Name: GAUGE_MONOMIAL
```

With the other script, this can be converted back:

```xml
<?xml version='1.0' encoding='utf-8'?>
<Params>
  <MCControl>
    <Cfg>
      <cfg_type>DISORDERED</cfg_type>
      <cfg_file>DUMMY</cfg_file>
    </Cfg>
    <RNG>
      <Seed>
        <elem>11</elem>
        <elem>0 </elem>
        <elem>0 </elem>
        <elem>0 </elem>
      </Seed>
    </RNG>
    <StartUpdateNum>0</StartUpdateNum>
    <NWarmUpUpdates>0</NWarmUpUpdates>
    <NProductionUpdates>100</NProductionUpdates>
    <NUpdatesThisRun>100</NUpdatesThisRun>
    <SaveInterval>1</SaveInterval>
    <SavePrefix>wilson-clover</SavePrefix>
    <SaveVolfmt>SINGLEFILE</SaveVolfmt>
    <InlineMeasurements>
      <elem>
        <Name>POLYAKOV_LOOP</Name>
        <Frequency>1</Frequency>
        <Param>
          <version>2</version>
        </Param>
        <NamedObject>
          <gauge_id>default_gauge_field</gauge_id>
        </NamedObject>
      </elem>
    </InlineMeasurements>
  </MCControl>
  <HMCTrj>
    <Monomials>
      <elem>
        <Name>GAUGE_MONOMIAL</Name>
```

The comments and blank lines are lost. Still one can now use either format to
write or view the input/output files.
