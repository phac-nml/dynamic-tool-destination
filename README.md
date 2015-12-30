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
```git clone git@gitlab.corefacility.ca:nml/dynamic-tool-destination.git```

2. In the root directory of this project on the command line, type in:
```make install GALAXY_PATH="your-galaxy-path"```

**Note**: To simply update your copy of Dynamic Tool Destination with the latest version, but
keep the same configuration file, you may use ```make upgrade GALAXY_PATH="your-galaxy-path"```

3. Make sure you read https://wiki.galaxyproject.org/Admin/Config/Jobs for instructions on
how to set up job_conf.xml.

4. In the ```<destinations>``` section, add the following to make sure Galaxy sees
DynamicToolDestination:
```
<destination id="dynamic_destination" runner="dynamic">  
        <param id="type">python</param>  
        <param id="function">map_tool_to_destination</param>  
</destination>
```

5. Change the default destination to use Dynamic Tool Destination:  
In the header for the destinations section, ensure that it reads ```<destinations default="dynamic_destination">```  
With Dynamic Tool Destination as the default, you can simply add new tools to this program's config
along with its rules.


Putting it all together, here's a real-world example tool_conf.xml following the steps
outlined above, followed by how it's used when called from Galaxy:
```
<?xml version="1.0"?>
<job_conf>
    <plugins>
        <plugin id="local" type="runner" load="galaxy.jobs.runners.local:LocalJobRunner" workers="4"/>
        <plugin id="drmaa" type="runner" load="galaxy.jobs.runners.drmaa:DRMAAJobRunner" workers="6"/>
    </plugins>
    <handlers default="handlers">
        <handler id="main" tags="handlers"/>
    </handlers>
    <destinations default="dynamic_destination">
        <destination id="local" runner="local"/>

        <destination id="dynamic_destination" runner="dynamic">
            <param id="type">python</param>
            <param id="function">map_tool_to_destination</param>
        </destination>

        <destination id="cluster_default" runner="drmaa">
            <param id="nativeSpecification">-q test.q </param>
        </destination>

        <destination id="cluster_low_32" runner="drmaa">
            <param id="nativeSpecification">-q test.q -pe galaxy 32 -l h_vmem=2G</param>
        </destination>

        <destination id="cluster_low_24" runner="drmaa">
            <param id="nativeSpecification">-q test.q -pe galaxy 24 -l h_vmem=2G</param>
        </destination>

        <destination id="cluster_low_16" runner="drmaa">
            <param id="nativeSpecification">-q test.q -pe galaxy 16 -l h_vmem=2G</param>
        </destination>
    </destinations>
</job_conf>
```

Suppose a researcher is attempting to use the tool spades with two fastqsanger files.
Based on the rules outlined in Dynamic Tool Destination's configuration, this program
may decide that her files are eligible for use on cluster_low_32. This XML file is then
checked to see if such destination with an ID of ```cluster_low_32``` exists. If it does,
the arguments contained inside the destination's params are passed to the cluster.
In this case, the job would be run with parameters ```-q test.q -pe galaxy 32 -l h_vmem=2G```


## Testing  
---
To run the test suit on this project, from the root directory in the
command line, type tox.  
**Note**: Tox version 1.6.0 or greater is required!

To run specific parts of the testing:

1. To run python 2.6 tests
```
tox -e py26
```

2. To run python 2.7 tests
```
tox -e py27
```

3. To run flake tests
```
tox -e flake8
```

## Configuration  
---
The configuration for each tool is done in tool_destinations.yml. You may either edit
this file in the root folder and run make clean then make install, or you can
edit this file directly in galaxy_path/config/tool_destinations.yml

The configuration will have three main levels (or key properties) - ```tools```, 
```default_destination```, and ```verbose```.

Under ```tools``` is where you put the IDs of the tools. Tool IDs must be
distinct. In each tool is a list of rules, each of which contain rule-specific
paremeters. DynamicToolDestination.py is set up to allow and fix a few light errors
in the config, but it's best to follow the specified template.

```default_destination```, the second key property, specifies which global destination 
to default to in case none of the rules apply. 

A third key property is ```verbose```. When this is set to True, Dynamic Tool Destination
gives much more descriptive output regarding the steps it's taking in mapping your tools to
the appropriate destinations, including config validation and any potential errors found in the
config.

The general template is as follows (note that this template
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
        destination: cluster_low_4
      - rule_type: file_size
        nice_value: 0
        lower_bound: 2 GB
        upper_bound: 4 GB
        destination: cluster_low_8
      - rule_type: file_size
        nice_value: 0
        lower_bound: 4 GB
        upper_bound: Infinity
        destination: cluster_low_16
    default_destination: cluster_default
default_destination: this global field is mandatory
verbose: True

```

Looking at this example, some things must be clarified: each entry in the list of
rules per tool is specified by '-'. Per rule, regardless of rule type,
the following fields are mandatory:
rule_type, nice_value, and destination.

Some of the other fields are mandatory only for specific rule types, which will be
further discussed below.

Starting with rule_type, there are currently 4 rule types: file_size, num_input_datasets, records,
and arguments.

file_size rules are based on how large the files are: if they fall
within specified limits, then the rule is satisfied, and the tool may proceed
with the appropriate destination.

Similarly, records rules are based on how many records are in the supplied ```.fasta``` files
and num_input_datasets rules are based on how many files are submitted.

file_size, num_input_datasets, and records rules have the following required parameters on top of the base
mandatory parameters:
upper_bound
lower_bound

Bounds are allowed to be specified in bytes (48000 for example) or a higher size unit,
including the unit abbreviation (4 GB or 10 TB for file_size, for example). Additionally, upper_bound
is allowed to be Infinite; simply specify Infinite in order to do so.

**The rule will allow the lower_bound, up to but not including the upper_bound  

The fourth rule_type is arguments, which has arguments as a mandatory parameter ontop of
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
    default_destination: cluster_low
default_destination: cluster
verbose: False
```

Next up, nice_value is used for prioritizing rules over others in case two rules
match. nice_value basically translates to, "the higher the nice_value, the 'nicer'
the tool is about being picked last". So based off of that idea, a rule with a nice
value of -5 is guaranteed to be picked over a rule with a nice value of 10. nice_value
is allowed to go from -20 to 20. If two rules have the same nice value and both were
satisfied, the first rule in the config file will be picked. In summary, first-come-
first-serve basis unless nice_value overrides that.

Additionally, the administrator can optionally specify a users list for each rule in order to 
grant or deny access to the specific rule (for example, using a certain cluster configuration
that is only intended for users running critical jobs). The users list is then simply a list of 
user email addresses, which Dynamic Tool Destination checks against when running jobs:

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
        users:
          - test@email.com
          - sample@corporate.ca
    default_destination: cluster_low
default_destination: cluster
verbose: False
```

A list of users may be passed into any rule type, and Dynamic Tool Destination 
checks the user submitting the job against the provided list of users to confirm access.

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

## Usage  
---

Assuming it is correctly installed, Dynamic Tool Destination should automatically assign
destinations to your jobs if the tool and eligible rules are specified in the config.

Dynamic Tool Destination can also be used directly to verify that your config file is
correctly formatted and meets all parameter requirements:

Assuming Dynamic Tool Destination is installed in Galaxy, and the config is located in
the ```galaxy/config``` directory, you can simply navigate to where Dynamic Tool
Destination is installed: ```galaxy/lib/galaxy/jobs/rules/``` and run it with a
```-c``` flag (or ```--check-config```).

For example:

```
python DynamicToolDestination.py -c
```

Alternatively, if you want to verify a config that is not located in galaxy/config, you
can simply provide the tool with a path to the config:

```
python DynamicToolDestination.py -c /path/to/tool_destinations.yml
```

Note that the output when running Dynamic Tool Destination from a commandline depends on
whether or not you have ```verbose``` turned on. It is advisable to turn it on for checking configs
as it gives descriptive error messages if issues are encountered.

## Contact
---

**Eric Enns**: eric.enns@phac-aspc.gc.ca
=======
