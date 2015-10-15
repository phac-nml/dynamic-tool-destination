# Dynamic Tool Destination
---

## Legal
---

Dynamic Tool Destination

Copyright Government of Canada 2015

Written by: Eric Enns, Public Health Agency of Canada,
                       National Microbiology Laboratory
            Daniel Bouchard, Public Health Agency of Canada,
                       National Microbiology Laboratory

Funded by the National Micriobiology Laboratory

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Description
---
This project dynamically maps tools to destinations based on the following rules, file_size, records, arguments.


## Installation  
---
1. Clone this repository:
		git clone git@gitlab.corefacility.ca:nml/dynamic-tool-destination.git

2. In the root directory of this project on the command line, type in:
		make install GALAXY_PATH="your-galaxy-path"


## Testing  
---
To run the test suit on this project, from the root directory in the  
command line, type tox. To run specific parts of the testing:

1. To run python 2.6 tests
```
tox -e py26
```

2. To run python 2.7 tests
```
tox -e py27
```

2. To run flake tests
```
tox -e flake8
```

## Configuration  
---
The configuration for each tool is done in tool_destinations.yml. You may either edit  
this file in the root folder and run make clean then make install, or you can  
edit this file directly in galaxy_path/config/tool_destinations.yml  

For each key-property under tools:, put the ID of the tool. Tool IDs must be  
distinct. In each tool is a list of rules, each of which contain rule-specific
paremeters. DynamicToolDestination.py is set up to allow and fix a few light errors
in the config, but it's best to follow the specified template.

There is a special key-property that goes in same the level as tools:,
default_destination, which specifies which global destination to default to in case
none of the rules apply. The general template is as follows (note that this template
does not use quote symbols), using spades and smalt as an example
(spades for showing what each field is for, and smalt
to give a fairly real-world example):

Ex:  
```
tools:
	spades:
		rules:
			- rule_type: what kind of rule is it?
				nice_value: what kind of priority does this rule have over others?
				destination: how should this tool be run?
				lower_bound: what's the max file size?
				upper_bound: what's the minimum file size?
		default_destination: this tool-specific field is optional
	smalt_map:
	  rules:
	    - rule_type: file_size
	      nice_value: 0
	      lower_bound: 0
	      upper_bound: 2 GB
	      destination: waffles_low_4
	    - rule_type: file_size
	      nice_value: 0
	      lower_bound: 2 GB
	      upper_bound: 4 GB
	      destination: waffles_low_8
	    - rule_type: file_size
	      nice_value: 0
	      lower_bound: 4 GB
	      upper_bound: Infinity
	      destination: waffles_low_16
	  default_destination: waffles_default
default_destination: this global field is mandatory

```

Looking at this example, some things must be clarified: each entry in the list of
rules per tool is specified by '-'. Per rule, regardless of rule type,
the following fields are mandatory:
rule_type, nice_value, and destination.

Some of the other fields are mandatory only for specific rule types, which will be
further discussed below.

Starting with rule_type, there are currently 3 rule types: file_size, records,
and arguments.

file_size and records rules are based on how large the files are: if they fall
within specified limits, then the rule is satisfied, and the tool may proceed
with the appropriate destination.

file_size and records rules have the following required parameters on top of the base
mandatory parameters:
upper_bound
lower_bound

Bounds are allowed to be specified in bytes (48000 for example) or a higher size unit,
including the unit abbreviation (4 GB or 10 TB for example). Additionally, upper_bound
is allowed to be Infinite; simply specify Infinite in order to do so.

**The rule will allow the lower_bound, up to but not including the upper_bound  

The third rule_type is arguments, which has arguments as a mandatory parameter ontop of
the base mandatory parameters. The arguments parameter is specified using the following
template:

```
arguments:
	argument_name: the_argument
```

A real world example is shown below:

```
tools:
  spades:
    rules:
      - rule_type: arguments
        nice_value: -19
        destination: fail
        fail_message: Don't do that
        arguments:
          careful: true
    default_destination: waffles_low
default_destination: waffles
```

Next up, nice_value is used for prioritizing rules over others in case two rules
match. nice_value basically translates to, "the higher the nice_value, the 'nicer'
the tool is about being picked last". So based off of that idea, a rule with a nice
value of -5 is guaranteed to be picked over a rule with a nice value of 10. nice_value
is allowed to go from -20 to 20. If two rules have the same nice value and both were
satisfied, the first rule in the config file will be picked. In summary, first-come-
first-serve basis unless nice_value overrides that.


Finally, destination simply refers to the specific way the tool will run. Each
destination ID refers to a specific configuration to run the tool with.

Some rules may call for the job to fail if certain conditions are encountered. In
this case, destination simply refers to 'fail'.

For example, the following rule is set to fail the job if a file that is too large
(more than 4GB) is encountered:

```
tools:
  spades:
		rules:
			- rule_type: file_size
				nice_value: 0
				destination: fail
				fail_message: Data too large
				lower_bound: 4 GB
				upper_bound: Infinity
```

As shown above, a rule with 'fail' as the destination requires an additional
parameter, 'fail_message', which DynamicToolDestination uses to print a helpful error
message to the user indicating why the job failed (showing up inside the job log in
Galaxy's history panel).

## Contact
---

**Eric Enns**: eric.enns@phac-aspc.gc.ca
