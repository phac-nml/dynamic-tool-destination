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
import collections


# log to galaxy"s logger
log = logging.getLogger(__name__)


class MalformedYMLException(Exception):
    pass


class ScannerError(Exception):
    pass


class RuleValidator:

    @classmethod
    def validate_rule(cls, rule_type, *args, **kwargs):
        if rule_type == 'file_size':
            return cls.__validate_file_size_rule(*args, **kwargs)

        elif rule_type == 'records':
            return cls.__validate_records_rule(*args, **kwargs)

        elif rule_type == 'arguments':
            return cls.__validate_arguments_rule(*args, **kwargs)

    @classmethod
    def __validate_file_size_rule(cls, rule, counter, tool):
        """
        Right now this function is doing all the heavy lifting for validating all of
        parameters for all rule_types. That's why it checks rule_type even though it's
        called 'file_size'.
        """

        # Nice Value Verification #
        if "nice_value" in rule:
            if rule["nice_value"] < -20 or rule["nice_value"] > 20:
                error = "Nice value goes from -20 to 20; rule " + str(counter)
                error += " in '" + str(tool) + "' has a nice value of '"
                error += str(rule["nice_value"]) + "'. Setting nice value to 0."
                log.debug(error)
                rule["nice_value"] = 0
        else:
            error = "No nice value found for rule " + str(counter) + " in '" + str(tool)
            error += "'. Setting nice value to 0."
            log.debug(error)
            rule["nice_value"] = 0

        # Destination Verification #
        if "fail_message" in rule:
            rule["destination"] = "fail"

        if "destination" in rule and isinstance(rule["destination"], str):
            if rule["destination"] == "fail" and "fail_message" not in rule:
                    error = "Missing a fail message for rule " + str(counter)
                    error += " in '" + str(tool) + "'. Adding generic fail message."
                    log.debug(error)
                    message = "Invalid parameters for rule " + str(counter)
                    message += " in '" + str(tool) + "'."
                    rule["fail_message"] = message
        else:
            error = "No destination specified for rule " + str(counter)
            error += " in '" + str(tool) + "'. Ignoring..."
            log.debug(error)

        # Bounds Verification #
        if rule["rule_type"] == "file_size" or rule["rule_type"] == "records":
            if "upper_bound" in rule and "lower_bound" in rule:
                upper_bound = str_to_bytes(rule["upper_bound"])
                lower_bound = str_to_bytes(rule["lower_bound"])

                if upper_bound != -1 and lower_bound > upper_bound:
                    error = "Lower bound exceeds upper bound for rule " + str(counter)
                    error += " in '" + str(tool) + "'. Reversing bounds."
                    log.debug(error)
                    temp_upper_bound = rule["upper_bound"]
                    temp_lower_bound = rule["lower_bound"]
                    rule["upper_bound"] = temp_lower_bound
                    rule["lower_bound"] = temp_upper_bound
            else:
                error = "Missing bounds for rule " + str(counter)
                error += " in '" + str(tool) + "'. Ignoring rule."
                log.debug(error)
                rule["rule_type"] = "fail"

        # Arguments Verification (for rule_type arguments; read comment block at top
        # of function for clarification.
        if rule["rule_type"] == "arguments":
            if "arguments" not in rule or not isinstance(rule["arguments"], dict):
                error = "No arguments found for rule " + str(counter) + " in '"
                error += str(tool) + "' despite being of type arguments. Ignoring rule."
                log.debug(error)
                rule["rule_type"] = "fail"

        return rule

    @classmethod
    def __validate_records_rule(cls, rule, counter, tool):
        """
        This function exists so that in the future, if records accepts differing
        parameters than file_size, then you could simply edit this function. But for now,
        since both rule_types share identical incoming parameters, I'll just pass this
        off to file_size
        """

        return cls.__validate_file_size_rule(rule, counter, tool)

    @classmethod
    def __validate_arguments_rule(cls, rule, counter, tool):
        """
        This function exists so that in the future, if arguments accepts differing
        parameters than file_size, then you could simply edit this function. But for now,
        since both rule_types share identical incoming parameters, I'll just pass this
        off to file_size
        """

        return cls.__validate_file_size_rule(rule, counter, tool)


def parse_yaml(path="/config/tool_options.yml", test=False):
    """
    Get a properly formatted yaml file from path.
    """
    # Import file from path
    try:
        if test:
            config = load(path)
        else:
            opt_file = os.getcwd() + path
            with open(opt_file, 'r') as stream:
                config = load(stream)

        # Test imported file
        try:
            config = validate_config(config)
        except MalformedYMLException:
            log.error(str(sys.exc_value))
            raise
    except ScannerError:
        log.error("YML file is too malformed to fix!")
        raise

    return config


def validate_config(obj):
    new_config = collections.defaultdict(lambda: collections.defaultdict(dict))
    log.debug("Running config validation...")

    available_rule_types = ['file_size', 'records', 'arguments']

    if obj is not None:
        for category in obj.keys():
            if category == "default_destination":
                if isinstance(obj[category], str):
                    new_config["default_destination"] = obj[category]

            elif category == "tools":
                for tool in obj[category]:
                    curr = obj[category][tool]

                    # This check is to make sure we have a tool name, and not just
                    # rules right way.
                    if not isinstance(curr, list):
                        curr_tool_rules = []

                        if curr is not None:
                            if ("default_destination" in curr and
                                    isinstance(curr['default_destination'], str)):
                                new_config[category][tool]['default_destination'] = (
                                    curr['default_destination'])

                            if "rules" in curr and isinstance(curr['rules'], list):
                                curr_tool = curr
                                counter = 0

                                for rule in curr_tool['rules']:
                                    if "rule_type" in rule:
                                        if rule['rule_type'] in available_rule_types:
                                            validated_rule = None
                                            counter += 1

                                            validated_rule = RuleValidator.validate_rule(
                                                rule['rule_type'], rule, counter, tool)

                                            if (validated_rule is not None and not
                                                    validated_rule['rule_type']
                                                    == "fail"):
                                                curr_tool_rules.append(
                                                    copy.deepcopy(validated_rule))

                                        else:
                                            error = "Unrecognized rule_type '"
                                            error += rule['rule_type'] + "' "
                                            error += "found in '" + str(tool) + "'. "
                                            error += "Ignoring..."
                                            log.debug(error)

                                    else:
                                        counter += 1
                                        error = "No rule type found for rule "
                                        error += str(counter)
                                        error += " in '" + str(tool) + "'."
                                        log.debug(error)
                            else:
                                error = "No rules found for '" + str(tool) + "'!"
                                log.debug(error)

                        if curr_tool_rules:
                            new_config[category][str(tool)]['rules'] = curr_tool_rules

                    else:
                        error = "Malformed YML; expected job name, "
                        error += "but found a list instead!"
                        log.debug(error)

            else:
                error = "Unrecognized category '" + category + "' found in config file!"
                log.debug(error)

    else:
        log.debug("No (or empty) config file supplied!")

    log.debug("Finished config validation.")

    return new_config


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

    # Get configuration from tool_options.yml
    try:
        config = parse_yaml(path)
    except MalformedYMLException as e:
        raise JobMappingException(e)

    matched_rule = None

    # For each different rule for the tool that's running
    fail_message = None

    if config is not None:
        if "default_destination" in config:
            destination = config['default_destination']
            config = config['tools']
            if str(tool.old_id) in config:
                for rule in config[str(tool.old_id)]['rules']:
                    # test if config[] is array
                    if rule["rule_type"] == "file_size":
                        upper_bound = str_to_bytes(rule["upper_bound"])
                        lower_bound = str_to_bytes(rule["lower_bound"])

                        if upper_bound == -1:
                            if lower_bound <= file_size:
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule
                        else:
                            if lower_bound <= file_size and file_size < upper_bound:
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

                    elif rule["rule_type"] == "records":
                        upper_bound = str_to_bytes(rule["upper_bound"])
                        lower_bound = str_to_bytes(rule["lower_bound"])

                        if upper_bound == -1:
                            if lower_bound <= records:
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

                        else:
                            if lower_bound <= records and records < upper_bound:
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

                    elif rule["rule_type"] == "arguments":
                        options = job.get_param_values(app)
                        matched = True
                        for arg in rule["arguments"]:
                            if arg in options:
                                if rule["arguments"][arg] != options[arg]:
                                    matched = False
                                    options = "test"
                            else:
                                matched = False
                                log.debug("Argument '" + str(arg) + "' not recognized!")

                            if matched is True:
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

            else:
                error = "Tool '" + str(tool.old_id) + "' not specified in config. "
                error += "Using default destination."
                log.debug(error)

            if matched_rule is None:
                if "default_destination" in config[str(tool.old_id)]:
                    destination = config[str(tool.old_id)]['default_destination']
            else:
                destination = matched_rule["destination"]

        else:
            destination = "fail"
            fail_message = "Job '" + str(tool.old_id) + "' failed; "
            fail_message += "no global default destination specified in YML file!"

    else:
        destination = "fail"
        fail_message = "No config file supplied!"

    if destination == "fail":
        if fail_message:
            raise JobMappingException(fail_message)
        else:
            raise JobMappingException(matched_rule["fail_message"])

    return destination
