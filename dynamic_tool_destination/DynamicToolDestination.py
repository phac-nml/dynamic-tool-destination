from __future__ import print_function

"""
# =============================================================================

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

# =============================================================================
"""

"""
Created on May 13, 2015

@author: Daniel Bouchard
"""

from yaml import load

import glob
import logging
import os
import sys
import copy
import string


class MalformedYMLException(Exception):
    pass


def parse_yaml(path="/config/tool_options.yml", test=False):
    """
    Get a properly formatted yaml file from path.
    """
    # Import file from path
    if test:
        tools = load(path)
    else:
        opt_file = os.getcwd() + path
        with open(opt_file, 'r') as stream:
            tools = load(stream)

    # Test imported file
    try:
        tools = test_tools(tools)
    except MalformedYMLException:
        log.error(str(sys.exc_value))
        raise

    return tools


def verify_config(obj, config_valid = True):
    new_config = {}

    for tool in obj.keys():
        if tool  == "default_destination" and isinstance(obj[tool], str):
            new_config[tool] = obj[tool]
            default_destination_present = True
        elif isinstance(obj[tool]['rules'], list):
            for rule in curr_tool['rules']:





        else:
            config_valid = False







def test_tools(obj):
    """
    Check object to see if it has the correct members to be used in job configuration.
    add option to fail if invalid, set to false by default
    have a value config_valid set to true by default, set it to false if anything is messed up
    default_destination is mandatory
    """
    obj_cp = copy.deepcopy(obj)
    new_config = {}

    # Loops through all tools
    try:
        for tool in obj_cp.keys():
            if tool == "default_destination":
                if obj[tool] is String:
                    new_config[tool]=obj[tool]
                # Check universal default for destination
                curr_tool = obj[tool]
                try:
                    rule_destination = curr_tool
                except (KeyError, TypeError):
                    raise MalformedYMLException("Error getting default destination.")
            else:
                curr_tool = obj_cp[tool]
                curr_tool_rules = []

                # at the end
                new_config[tool]['rules'] == curr_tool_rules
                # Loops through all rules for the current tool
                for rule in curr_tool['rules']:
                    curr_tool_rules.append(copy.deepcopy(rule)) #if the current rule passes
                    # Checks if the current rule has a type,
                    # and, from the type, checks for other parameters.
                    try:
                        try:
                            # Search for a type attribute
                            rule_type = rule["rule_type"]
                        except (KeyError, TypeError):
                            error = "Error getting " + str(rule)
                            error += " type for " + str(tool)
                            raise TypeError(error)

                        try:
                            # Search for a rule destination
                            rule_destination = rule["destination"]

                            if rule_destination == "fail":
                                try:
                                    rule["fail_message"]
                                except (KeyError, TypeError):
                                    error = "fail_message not set for current rule"
                                    error += " in " + str(tool)
                                    log.debug(error)
                        except (KeyError, TypeError):
                            error = "Error getting " + str(rule)
                            error += " destination in " + str(tool)
                            raise TypeError(error)

                        try:
                            if rule["nice_value"] < -20 or rule["nice_value"] > 20:
                                error_info = "Nice value goes from -20 to 20; "
                                error_info += "this rule's nice value is "
                                error_info += str(rule["nice_value"])
                                log.debug(error_info)
                                raise KeyError()
                        except KeyError:
                            error_resolve = "Invalid nice value. Setting "
                            error_resolve += tool + "'s rule's nice to 0."
                            rule["nice_value"] = 0
                            log.debug(error_resolve)

                        if rule_type == "file_size" or rule_type == "records":
                            # Test for file_size/records specific members
                            try:
                                rule["lower_bound"]
                            except (KeyError, TypeError):
                                error = "Error getting " + str(rule)
                                error += " lower_bound in " + str(tool)
                                raise TypeError(error)

                            try:
                                rule["upper_bound"]
                            except (KeyError, TypeError):
                                error = "Error getting " + str(rule)
                                error += " upper_bound in " + str(tool)
                                raise TypeError(error)

                        elif rule_type == "arguments":
                            # Test for parameter specific members
                            try:
                                rule["arguments"]
                            except KeyError:
                                error = "No arguments for " + str(rule)
                                error += " in " + str(tool)
                                raise TypeError(error)

                        else:
                            error = "Unrecognized rule type "
                            error += str(rule_type) + " in " + str(tool)
                            raise TypeError(error)
                    except TypeError as e:
                        log.error(e)
                        error = "YML file not properly formatted; errors found"
                        error += " in tool " + str(tool)
                        log.debug(error)

    except (AttributeError, TypeError):
        log.debug("Illegal object: " + str(obj))

    return obj_cp


def bytes_to_str(size, unit="YB"):
    '''
    Uses the bi convention: 1024 B = 1 KB since this method primarily
    has inputs of bytes for RAM
    '''
    # converts size in bytes to most readable unit
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = 0

    # mostly called in order to convert "infinity"
    try:
        size_changer = int(size)
    except ValueError:
        error = "bytes_to_str passed uncastable non numeric value "
        raise ValueError(error + str(size))

    try:
        upto = units.index(unit.strip().upper())
    except ValueError:
        upto = 9

    while size_changer >= 1024 and i < upto:
        size_changer = size_changer / 1024.0
        i += 1

    if size_changer == -1:
        size_changer = "Infinity"
        i = 0

    try:
        return_str = "%.2f %s" % (size_changer, units[i])
    except TypeError:
        return_str = "%s" % (size_changer)

    return return_str


def str_to_bytes(size):
    '''
    Uses the bi convention: 1024 B = 1 KB since this method primarily
    has inputs of bytes for RAM
    '''
    units = ["", "b", "kb", "mb", "gb", "tb", "pb", "eb", "zb", "yb"]
    curr_size = size
    try:
        if size.lower() != "infinity":
            # Get the number
            try:
                curr_item = size.strip().split(" ")
                curr_size = "".join(curr_item)

                curr_size = int(curr_size)
            except ValueError:
                curr_item = size.strip().split(" ")
                curr_unit = curr_item[-1].strip().lower()
                curr_item = curr_item[0:-1]
                curr_size = "".join(curr_item)
                curr_size = curr_size.translate(None, string.punctuation)

                try:
                    curr_size = int(curr_size)
                except ValueError:
                    error = "Unable to convert size " + str(size)
                    raise MalformedYMLException(error)

            # Get the unit and convert to bytes
            try:
                pos = units.index(curr_unit)
                for x in range(pos, 1, -1):
                    curr_size *= 1024
            except ValueError:
                error = "Unable to convert size " + str(size)
                raise MalformedYMLException(error)
            except (UnboundLocalError, NameError):
                pass
        else:
            curr_size = -1
    except AttributeError:
        # If size is not a string (doesn't have .lower())
        pass

    return curr_size


def importer(test):
    """
    Uses Mock galaxy for testing or real galaxy for production
    """
    global JobDestination
    global JobMappingException
    if test is not True:
        from galaxy.jobs import JobDestination
        from galaxy.jobs.mapper import JobMappingException
    else:
        from tests.mockGalaxy import JobDestination
        from tests.mockGalaxy import JobMappingException

# log to galaxy"s logger
log = logging.getLogger(__name__)


def map_tool_to_destination(
        job, app, tool, test=False, path="/config/tool_destinations.yml"):
    """
    Dynamically allocate resources
    """
    importer(test)

    # Get all inputs from tool and databases
    inp_data = dict([(da.name, da.dataset) for da in job.input_datasets])
    inp_data.update([(da.name, da.dataset) for da in job.input_library_datasets])
    file_size = 0
    records = 0

    try:
        # If you're going to the vfdb do this.
        for this_tool in tool.installed_tool_dependencies:
            if this_tool.name == "vfdb":
                bact = job.get_param_values(app, True)["mlst_or_genedb"]["vfdb_in"]
                instal_dir = str(this_tool.installation_directory(app))
                _file = glob.glob(instal_dir + "/vfdb/?" + bact[1:] + "*")
                inp_db = open(str(_file[0]))
                log.debug("Loading file: " + _file[0])
    except(KeyError, IndexError, TypeError):
        log.info("No virulence factors database")

    # Loop through the database and look for amount of records
    try:
        for line in inp_db:
            if line[0] == ">":
                records += 1
    except NameError:
        pass

    # Loop through each input file and adds the size to the total
    # or looks through db for records
    for da in inp_data:
        try:
            # If the input is a file, check and add the size
            if os.path.isfile(str(inp_data[da].file_name)):
                log.debug("Loading file: " + str(da) + str(inp_data[da].file_name))

                # Add to records if the file type is fasta
                if inp_data[da].datatype.file_ext == "fasta":
                    inp_db = open(inp_data[da].file_name)

                    # Try to find automatically computed sequences
                    metadata = inp_data[da].get_metadata()

                    try:
                        records += int(metadata.get("sequences"))
                    except (TypeError, KeyError):
                        for line in inp_db:
                            if line[0] == ">":
                                records += 1
                else:
                    query_file = str(inp_data[da].file_name)
                    file_size += os.path.getsize(query_file)
        except AttributeError:
            # Otherwise, say that input isn't a file
            log.debug("Not a file: " + str(inp_data[da]))

    log.debug("Total size: " + bytes_to_str(file_size))
    log.debug("Total amount of records: " + str(records))

    # Chooses tool based on tool

    # Get configuration from tool_options.yml
    try:
        config = parse_yaml(path)
    except MalformedYMLException as e:
        raise JobMappingException(e)

    matched_rule = None
    destination = config['default_destination']

    # For each different rule for the tool that's running
    for rule in config[str(tool.old_id)]['rules']:
        #test if config[] is array
        if rule["rule_type"] == "file_size":
            upper_bound = str_to_bytes(rule["upper_bound"])
            lower_bound = str_to_bytes(rule["lower_bound"])

            if upper_bound == -1:
                if lower_bound <= file_size:
                    if matched_rule is None or rule["nice_value"] < matched_rule["nice_value"]:
                        matched_rule = rule
            else:
                if lower_bound <= file_size and file_size < upper_bound:
                    if matched_rule is None or rule["nice_value"] < matched_rule["nice_value"]:
                        matched_rule = rule

        elif rule["rule_type"] == "records":
            upper_bound = str_to_bytes(rule["upper_bound"])
            lower_bound = str_to_bytes(rule["lower_bound"])

            if upper_bound == -1:
                if lower_bound <= records:
                    if matched_rule is None or rule["nice_value"] < matched_rule["nice_value"]:
                        matched_rule = rule

            else:
                if lower_bound <= records and records < upper_bound:
                    if matched_rule is None or rule["nice_value"] < matched_rule["nice_value"]:
                        matched_rule = rule

        elif rule["rule_type"] == "arguments":
            # TODO: This accepts the rule if any arguments are correct,
            #       we should probably change it to if all are correct

            options = job.get_param_values(app)
            matched = True
            for arg in rule["arguments"].keys():
                if arg in options:
                    if rule["arguments"][arg] != options[arg]:
                        matched = False
                else:
                    matched = False

                if matched is True:
                    if matched_rule is None or rule["nice_value"] < matched_rule["nice_value"]:
                        matched_rule = rule

    if matched_rule is None:
        if "default_destination" in config[str(tool.old_id)]:
            destination = config[str(tool.old_id)]['default_destination']
    else:
        destination = matched_rule["destination"]

    return destination
