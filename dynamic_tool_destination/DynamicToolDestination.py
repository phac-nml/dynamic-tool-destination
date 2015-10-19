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

import argparse
import glob
import logging
import os
import sys
import copy
import string
import collections


# log to galaxy's logger
log = logging.getLogger(__name__)


class MalformedYMLException(Exception):
    pass


class ScannerError(Exception):
    pass


class RuleValidator:
    """
    This class is the primary facility for validating configs. It's always called
    in map_tool_to_destination and it's called for validating config directly through
    DynamicToolDestination.py
    """

    @classmethod
    def validate_rule(cls, rule_type, return_result=False, *args, **kwargs):
        """
        This function is responsible for passing each rule to its relevant function.

        @type rule_type: str
        @param rule_type: the current rule's type

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @rtype: bool, dict (depending on return_result)
        @return: validated rule or result of validation (depending on return_result)
        """
        if rule_type == 'file_size':
            return cls.__validate_file_size_rule(return_result, *args, **kwargs)

        elif rule_type == 'records':
            return cls.__validate_records_rule(return_result, *args, **kwargs)

        elif rule_type == 'arguments':
            return cls.__validate_arguments_rule(return_result, *args, **kwargs)

    @classmethod
    def __validate_file_size_rule(
            cls, return_result, original_rule, counter, tool):
        """
        This function is responsible for validating 'file_size' rules.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool, dict (depending on return_result)
        @return: validated rule or result of validation (depending on return_result)
        """

        rule = copy.deepcopy(original_rule)
        result = True

        # Nice_value Verification #
        result, rule = cls.__validate_nice_value(
            result, return_result, rule, tool, counter)

        # Destination Verification #
        result, rule = cls.__validate_destination(
            result, return_result, rule, tool, counter)

        # Bounds Verification #
        result, rule = cls.__validate_bounds(
            result, return_result, rule, tool, counter)

        if return_result:
            return result

        else:
            return rule

    @classmethod
    def __validate_records_rule(cls, return_result, original_rule, counter, tool):
        """
        This function is responsible for validating 'records' rules.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool, dict (depending on return_result)
        @return: validated rule or result of validation (depending on return_result)
        """

        rule = copy.deepcopy(original_rule)
        result = True

        # Nice_value Verification #
        result, rule = cls.__validate_nice_value(
            result, return_result, rule, tool, counter)

        # Destination Verification #
        result, rule = cls.__validate_destination(
            result, return_result, rule, tool, counter)

        # Bounds Verification #
        result, rule = cls.__validate_bounds(result, return_result, rule, tool, counter)

        if return_result:
            return result

        else:
            return rule

    @classmethod
    def __validate_arguments_rule(
            cls, return_result, original_rule, counter, tool):
        """
        This is responsible for validating 'arguments' rules.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool, dict (depending on return_result)
        @return: validated rule or result of validation (depending on return_result)
        """

        rule = copy.deepcopy(original_rule)
        result = True

        # Nice_value Verification #
        result, rule = cls.__validate_nice_value(
            result, return_result, rule, tool, counter)

        # Destination Verification #
        result, rule = cls.__validate_destination(
            result, return_result, rule, tool, counter)

        # Arguments Verification (for rule_type arguments; read comment block at top
        # of function for clarification.
        result, rule = cls.__validate_arguments(
            result, return_result, rule, tool, counter)

        if return_result:
            return result

        else:
            return rule

    @classmethod
    def __validate_nice_value(cls, result, return_result, rule, tool, counter):
        """
        This function is responsible for validating nice_value.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type result: bool
        @param result: returns True if everything is valid. False if it encounters any
                       abnormalities in the config.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool, dict (tuple)
        @return: validated rule and result of validation
        """

        if "nice_value" in rule:
            if rule["nice_value"] < -20 or rule["nice_value"] > 20:
                error = "nice_value goes from -20 to 20; rule " + str(counter)
                error += " in '" + str(tool) + "' has a nice_value of '"
                error += str(rule["nice_value"]) + "'."
                if not return_result:
                    error += " Setting nice_value to 0."
                    rule["nice_value"] = 0
                log.debug(error)
                result = False

        else:
            error = "No nice_value found for rule " + str(counter) + " in '" + str(tool)
            error += "'."
            if not return_result:
                error += " Setting nice_value to 0."
                rule["nice_value"] = 0
            log.debug(error)
            result = False

        return result, rule

    @classmethod
    def __validate_destination(cls, result, return_result, rule, tool, counter):
        """
        This function is responsible for validating destination.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type result: bool
        @param result: returns True if everything is valid. False if it encounters any
                       abnormalities in the config.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool, dict (tuple)
        @return: validated rule and result of validation
        """

        if "fail_message" in rule:
            if "destination" not in rule or rule['destination'] != "fail":
                result = False

            rule["destination"] = "fail"

        if "destination" in rule and isinstance(rule["destination"], str):
            if rule["destination"] == "fail" and "fail_message" not in rule:
                    error = "Missing a fail_message for rule " + str(counter)
                    error += " in '" + str(tool) + "'."
                    if not return_result:
                        error += " Adding generic fail_message."
                        message = "Invalid parameters for rule " + str(counter)
                        message += " in '" + str(tool) + "'."
                        rule["fail_message"] = message
                    log.debug(error)
                    result = False
        else:
            error = "No destination specified for rule " + str(counter)
            error += " in '" + str(tool) + "'."
            if not return_result:
                error += " Ignoring..."
            log.debug(error)
            result = False

        return result, rule

    @classmethod
    def __validate_bounds(cls, result, return_result, rule, tool, counter):
        """
        This function is responsible for validating bounds.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type result: bool
        @param result: returns True if everything is valid. False if it encounters any
                       abnormalities in the config.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool/None, dict (tuple)
        @return: validated rule (or None if invalid) and result of validation
        """

        if "upper_bound" in rule and "lower_bound" in rule:
            upper_bound = str_to_bytes(rule["upper_bound"])
            lower_bound = str_to_bytes(rule["lower_bound"])

            if upper_bound != -1 and lower_bound > upper_bound:
                error = "lower_bound exceeds upper_bound for rule " + str(counter)
                error += " in '" + str(tool) + "'."
                if not return_result:
                    error += " Reversing bounds."
                    temp_upper_bound = rule["upper_bound"]
                    temp_lower_bound = rule["lower_bound"]
                    rule["upper_bound"] = temp_lower_bound
                    rule["lower_bound"] = temp_upper_bound
                log.debug(error)
                result = False

        else:
            error = "Missing bounds for rule " + str(counter)
            error += " in '" + str(tool) + "'."
            if not return_result:
                error += " Ignoring rule."
                rule = None
            log.debug(error)
            result = False

        return result, rule

    @classmethod
    def __validate_arguments(cls, result, return_result, rule, tool, counter):
        """
        This function is responsible for validating arguments.

        @type return_result: bool
        @param return_result: True when we are only interested in the result of the
                              validation, and not the validated rule itself.

        @type result: bool
        @param result: returns True if everything is valid. False if it encounters any
                       abnormalities in the config.

        @type original_rule: dict
        @param original_rule: contains the original received rule

        @type counter: int
        @param counter: this counter is used to identify what rule # is currently being
                        validated. Necessary for log output.

        @type tool: str
        @param tool: the name of the current tool. Necessary for log output.

        @rtype: bool/None, dict (tuple)
        @return: validated rule (or None if invalid) and result of validation
        """

        if "arguments" not in rule or not isinstance(rule["arguments"], dict):
            error = "No arguments found for rule " + str(counter) + " in '"
            error += str(tool) + "' despite being of type arguments."
            if not return_result:
                error += " Ignoring rule."
                rule = None
            log.debug(error)
            result = False

        return result, rule


def parse_yaml(path="/config/tool_destinations.yml", test=False, return_result=False):
    """
    Get a yaml file from path and send it to validate_config for validation.

    @type path: str
    @param path: the path to the config file

    @type test: bool
    @param test: indicates whether to run in test mode or production mode

    @type return_result: bool
    @param return_result: True when we are only interested in the result of the
                          validation, and not the validated rule itself.

    @rtype: bool, dict (depending on return_result)
    @return: validated rule or result of validation (depending on return_result)

    """
    # Import file from path
    try:
        if test:
            config = load(path)
        else:
            if path == "/config/tool_destinations.yml":
                opt_file = os.getcwd() + path

            else:
                opt_file = path

            with open(opt_file, 'r') as stream:
                config = load(stream)

        # Test imported file
        try:
            if return_result:
                result = validate_config(config, return_result)
            else:
                config = validate_config(config)
        except MalformedYMLException:
            log.error(str(sys.exc_value))
            raise
    except ScannerError:
        log.error("YML file is too malformed to fix!")
        raise

    if return_result:
        return result

    else:
        return config


def validate_config(obj, return_result=False):
    """
    Validate received config.

    @type obj: dict
    @param obj: the entire contents of the config

    @type return_result: bool
    @param return_result: True when we are only interested in the result of the
                          validation, and not the validated rule itself.

    @rtype: bool, dict (depending on return_result)
    @return: validated rule or result of validation (depending on return_result)
    """

    # Allow new_config to expand automatically when adding values to new levels
    new_config = collections.defaultdict(lambda: collections.defaultdict(dict))

    if not return_result:
        log.debug("Running config validation...")

    config_valid = True
    result = True

    # a list with the available rule_types. Can be expanded on easily in the future
    available_rule_types = ['file_size', 'records', 'arguments']

    if obj is not None:

        # in obj, there should always be only 2 categories: tools and default_destination
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

                            # in each tool, there should always be only 2 sub-categories:
                            # default_destination (not mandatory) and rules (mandatory)
                            if ("default_destination" in curr and
                                    isinstance(curr['default_destination'], str)):
                                new_config[category][tool]['default_destination'] = (
                                    curr['default_destination'])

                            if "rules" in curr and isinstance(curr['rules'], list):

                                # under rules, there should only be a list of rules
                                curr_tool = curr
                                counter = 0

                                for rule in curr_tool['rules']:
                                    if "rule_type" in rule:
                                        if rule['rule_type'] in available_rule_types:
                                            validated_rule = None
                                            counter += 1

                                            # if we're only interested in the result of
                                            # the validation, then only retrieve the
                                            # result
                                            if return_result:
                                                result = RuleValidator.validate_rule(
                                                    rule['rule_type'], return_result,
                                                    rule, counter, tool)

                                            # otherwise, retrieve the processed rule
                                            else:
                                                validated_rule = (
                                                    RuleValidator.validate_rule(
                                                        rule['rule_type'],
                                                        return_result,
                                                        rule, counter, tool))

                                            # if the result we get is False, then
                                            # indicate that the whole config is invalid
                                            if not result:
                                                config_valid = False

                                            # if we got a rule back that seems to be
                                            # valid (or was fixable) then append it to
                                            # list of ready-to-use tools
                                            if (not return_result
                                                    and validated_rule is not None):
                                                curr_tool_rules.append(
                                                    copy.deepcopy(validated_rule))

                                        # if rule['rule_type'] in available_rule_types
                                        else:
                                            error = "Unrecognized rule_type '"
                                            error += rule['rule_type'] + "' "
                                            error += "found in '" + str(tool) + "'. "
                                            if not return_result:
                                                error += "Ignoring..."
                                            log.debug(error)
                                            config_valid = False

                                    # if "rule_type" in rule
                                    else:
                                        counter += 1
                                        error = "No rule_type found for rule "
                                        error += str(counter)
                                        error += " in '" + str(tool) + "'."
                                        log.debug(error)
                                        config_valid = False

                            # if "rules" in curr and isinstance(curr['rules'], list)
                            else:
                                error = "No rules found for '" + str(tool) + "'!"
                                log.debug(error)
                                config_valid = False

                        # if curr is not None:
                        if curr_tool_rules:
                            new_config[category][str(tool)]['rules'] = curr_tool_rules

                    # if not isinstance(curr, list)
                    else:
                        error = "Malformed YML; expected job name, "
                        error += "but found a list instead!"
                        log.debug(error)
                        config_valid = False

            # if category == "default_destination"
            else:
                error = "Unrecognized category '" + category + "' found in config file!"
                log.debug(error)
                config_valid = False

    # if obj is not None
    else:
        log.debug("No (or empty) config file supplied!")
        config_valid = False

    if not return_result:
        log.debug("Finished config validation.")

    if return_result:
        return config_valid

    else:
        return new_config


def bytes_to_str(size, unit="YB"):
    '''
    Uses the bi convention: 1024 B = 1 KB since this method primarily
    has inputs of bytes for RAM

    @type size: int
    @param size: the size in int (bytes) to be converted to str

    @rtype: str
    @return return_str: the resulting string
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

    @type size: str
    @param size: the size in str to be converted to int (bytes)

    @rtype: int
    @return curr_size: the resulting size converted from str
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

    @type test: bool
    @param test: True when being run from a test
    """
    global JobDestination
    global JobMappingException
    if test:
        from tests.mockGalaxy import JobDestination
        from tests.mockGalaxy import JobMappingException
    else:
        from galaxy.jobs import JobDestination
        from galaxy.jobs.mapper import JobMappingException


def map_tool_to_destination(
        job, app, tool, test=False, path="/config/tool_destinations.yml"):
    """
    Dynamically allocate resources

    @param job: galaxy job
    @param app: current app
    @param tool: current tool

    @type test: bool
    @param test: True when running in test mode

    @type path: str
    @param path: path to tool_destinations.yml
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
                install_dir = str(this_tool.installation_directory(app))
                _file = glob.glob(install_dir + "/vfdb/?" + bact[1:] + "*")
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

    # Get configuration from tool_destinations.yml
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
                    if rule["rule_type"] == "file_size":

                        # bounds comparisons
                        upper_bound = str_to_bytes(rule["upper_bound"])
                        lower_bound = str_to_bytes(rule["lower_bound"])

                        if upper_bound == -1:
                            if lower_bound <= file_size:
                                # nice_value comparisons
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule
                        else:
                            if lower_bound <= file_size and file_size < upper_bound:
                                # nice_value comparisons
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

                    elif rule["rule_type"] == "records":

                        # bounds comparisons
                        upper_bound = str_to_bytes(rule["upper_bound"])
                        lower_bound = str_to_bytes(rule["lower_bound"])

                        if upper_bound == -1:
                            if lower_bound <= records:
                                # nice_value comparisons
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

                        else:
                            if lower_bound <= records and records < upper_bound:
                                # nice_value comparisons
                                if (matched_rule is None or rule["nice_value"]
                                        < matched_rule["nice_value"]):
                                    matched_rule = rule

                    elif rule["rule_type"] == "arguments":
                        options = job.get_param_values(app)
                        matched = True

                        # check if the args in the config file are available
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

            # if str(tool.old_id) in config
            else:
                error = "Tool '" + str(tool.old_id) + "' not specified in config. "
                error += "Using default destination."
                log.debug(error)

            if matched_rule is None:
                if "default_destination" in config[str(tool.old_id)]:
                    destination = config[str(tool.old_id)]['default_destination']
            else:
                destination = matched_rule["destination"]

        # if "default_destination" in config
        else:
            destination = "fail"
            fail_message = "Job '" + str(tool.old_id) + "' failed; "
            fail_message += "no global default destination specified in YML file!"

    # if config is not None
    else:
        destination = "fail"
        fail_message = "No config file supplied!"

    if destination == "fail":
        if fail_message:
            raise JobMappingException(fail_message)
        else:
            raise JobMappingException(matched_rule["fail_message"])

    return destination

if __name__ == '__main__':
    """
    This function is responsible for running the app if directly run through the
    commandline. It offers the ability to specify a config through the commandline
    for checking whether or not it is a valid config. It's to be run from within Galaxy,
    assuming it is installed correctly within the proper directories in Galaxy, and it
    looks for the config file in galaxy/config/. It can also be run with a path pointing
    to a config file if not being run directly from inside Galaxy install directory.
    """

    parser = argparse.ArgumentParser()
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    parser.add_argument(
        '-v', '--validate-config', dest='validate', nargs='?',
        help='Use this option to validate tool_destinations.yml.'
        + ' Specify file/path/to/tool_destinations.yml or'
        + ' store tool_destinations.yml in galaxy/config if running'
        + ' without a filepath argument.')

    args = parser.parse_args()

    # if run with no arguments, display the help message
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.validate:
        result = parse_yaml(path=args.validate, return_result=True)

    else:
        # go back 4 directories to the root directory of the Galaxy install
        os.chdir('../../../..')
        result = parse_yaml(path="/config/tool_destinations.yml", return_result=True)

    if result:
        print("Configuration is valid!")
    else:
        print("Errors detected; config not valid!")
