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

## Example

The script below can be used to print out the values contained in a generic data message.
(If you have a compact data message,
then using `compact_data_message_reader` instead of `generic_data_message_reader` should also work.)
Assuming the script is saved as `read-sdmx-values.py",
it can be used like so:

    python read-sdmx-values.py path/to/generic-data-message.xml path/to/dsd.xml
    
```python
import sys

import sdmx


def main():
    dataset_path = sys.argv[1]
    dsd_path = sys.argv[2]
    
    with open(dataset_path) as dataset_fileobj:
        with open(dsd_path) as dsd_fileobj:
            dataset_reader = sdmx.generic_data_message_reader(
                fileobj=dataset_fileobj,
                dsd_fileobj=dsd_fileobj,
            )
            _print_values(dataset_reader)


def _print_values(dataset_reader):
    for dataset in dataset_reader.datasets():
        key_family = dataset.key_family()
        name = key_family.name(lang="en")
        
        print name
        
        dimension_names = key_family.describe_dimensions(lang="en") + ["Time", "Value"]
        
        for series in dataset.series():
            row_template = []
            key = series.describe_key(lang="en")
            for key_name, key_value in key.iteritems():
                row_template.append(key_value)
            
            for observation in series.observations(lang="en"):
                row = row_template[:]
                row.append(observation.time)
                row.append(observation.value)
                
                print zip(dimension_names, row)

main()
```
