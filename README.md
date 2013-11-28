# SDMX

Read SDMX XML files.
I've only added the features I've needed,
so this is far from being a thorough implementation.
Contributions welcome.

## Installation

`pip install sdmx`

## Usage

### `sdmx.generic_data_message_reader(fileobj)`

Given a file-like object representing the XML of a generic data message,
return a data message reader.

### `sdmx.compact_data_message_reader(fileobj)`

Given a file-like object representing the XML of a compact data message,
return a data message reader.

### Data message readers

Each data message reader has the following attributes:

* `datasets()`: returns an iterable of `DatasetReader` instances.
  Each instance corresponds to a `<DataSet>` element.

### `DatasetReader`

A `DatasetReader` has the following attributes:

* `key_family()`: returns the `KeyFamily` for the dataset.
  This corresponds to the `<KeyFamilyRef>` element.

* `series()`: returns an iterable of `Series` instances.
  Each instance corresponds to a `<Series>` element.

### `KeyFamily`

A `KeyFamily` has the following attributes:

* `name(lang)`: the name of the key family in the language `lang`.

* `describe_dimensions(lang)`:
  for each dimension of the key family,
  find the referenced concept and use its name in the language `lang`.
  Returns a list of strings in the same order as in the source file.

### `Series`

A `Series` has the following attributes:

* `describe_key(lang)`:
  the key of a series is a mapping from each dimension of the dataset to a value.
  For instance, if the dataset has a dimension named `Country`,
  the value for the series might be `United Kingdom`.
  Returns an ordered dictionary mapping strings to lists of strings.
  For instance, if the dataset has a single dimension called `Country`,
  the returned value would be `{"Country": ["United Kingdom"]}`.
  All ancestors of a value are also described, with ancestors appearing before descendents.
  For instance, if the value `United Kingdom` has the parent value `Europe`,
  which has the parent value `World`,
  the returned value would be `{"Country": ["World", "Europe", "United Kingdom"]}`.
  
* `observations()`: returns an iterable of `Observation` instances.
  Each instance corresponds to an `<Obs>` element.
  
### `Observation`

An `Observation` has the following attributes:

* `time`
* `value`

