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
The configuration for each tool is done in tool_options. You may either edit  
this file in the root folder and run make clean then make install, or you can  
edit this file directly in galaxy_path/config/tool_options.yml  

For each key-property under Tools, put the ID of the tool. They must be  
distinct. In each tool the names of the conditions must also be distinct.  
If they are not distinct names then the program will overwrite any previous  
conditions with the latest defined condition. There is a special  
key-property that goes in the same place as a tool, default. It has two  
nested key-properties, destinationID and runner. The runner key-property  
defines the default runner type for all tools and the destinationID  
key-property defines the default location for tools to run on.  

Ex:  
```
spades:  
	cond1:  
	cond2:  
spades2:  
	cond1:  
default:  
	destinationID:  
	runner:  
```


For each condition key-property, there are two mandatory key-properties,  
"type" and "action". "type" stores the type of condition (filesize, record,  
parameter, or default) and the "action" key-property stores either location  
to run the tool on or "fail", which makes the job raise an error.  

Ex:  
```
condition:  
	type: "default"  
	action: "X"  
```


For each filesize and record type, there are two more mandatory  
key-properties, "lbound" and "hbound". "lbound" key-property stores a lower  
size bound for the input, and the "hbound" key-property stores a higher  
size bound for the input. For an infinitely large "hbound", put -1. "hbound"  
and "lbound" should either be a plain number or a string with a number a  
space and then a unit in bytes.  

Ex:  
```
condition:  
	type: "filesize"  
	lbound: "100"  
	hbound: "5 PB"  
	action: "fail"  
```
**The comparisons will include the lbound, up to but not including the hbound  


For each parameter type condition, there is one more mandatory  
key-property, "args". "args" is a list of parameters and values to look  
for in the tools parameters, as defined by it's xml. If any of those  
parameters are found, the "action" key-property is executed  

Ex:  
```
condition_args:  
	type: "parameter"  
	args:  
		careful: true  
	action: "fail"  
```


For parameter, filesize, and records type conditions, there is an optional  
"nice" key-property. This property will tell the program which condition  
has priority. The "nice" key-property defaults to zero. In the event that  
the "nice" key-property is the same in two contending conditions, the  
priority is given to the condition which appears first in the tool_options  
yaml file.  

Ex:  
```
condition3:  
	type: "records"  
	nice: "0"  
	lbound: "1000"   
	hbound: "10000"  
	action: "CCC"  
```


There is an optional err_msg key-property which will be displayed to the  
user in the event of a action key-property being fail.  

Ex:   
```
condition:  
	type: "default"  
	err_msg: "I failed."  
	action: "fail"  
```

## Contact
---

**Eric Enns**: eric.enns@phac-aspc.gc.ca
