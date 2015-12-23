# ===============================================================================
# 
# Copyright Government of Canada 2015
# 
# Written by: Eric Enns, Public Health Agency of Canada,
#                        National Microbiology Laboratory
#             Daniel Bouchard, Public Health Agency of Canada,
#                        National Microbiology Laboratory
# 
# Funded by the National Micriobiology Laboratory
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this work except in compliance with the License. You may obtain a copy of the
# License at:
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# 
# ===============================================================================
#
####################################
# author: Daniel Bouchard          #
# creation date: Jun. 22nd, 2015   #
####################################
GALAXY_PATH=./galaxy

all:none

test:
	make install
	test -e $(GALAXY_PATH)/config/tool_destinations.yml
	test -e $(GALAXY_PATH)/lib/galaxy/jobs/rules/DynamicToolDestination.py
	make clean
	! test -e $(GALAXY_PATH)/config/tool_destinations.yml
	! test -e $(GALAXY_PATH)/lib/galaxy/jobs/rules/DynamicToolDestination.py

install:
	cp ./dynamic_tool_destination/DynamicToolDestination.py $(GALAXY_PATH)/lib/galaxy/jobs/rules/
	cp ./dynamic_tool_destination/tool_destinations.yml $(GALAXY_PATH)/config/

upgrade:
	cp ./dynamic_tool_destination/DynamicToolDestination.py $(GALAXY_PATH)/lib/galaxy/jobs/rules/

clean:
	rm $(GALAXY_PATH)/lib/galaxy/jobs/rules/DynamicToolDestination.py
	rm $(GALAXY_PATH)/config/tool_destinations.yml
