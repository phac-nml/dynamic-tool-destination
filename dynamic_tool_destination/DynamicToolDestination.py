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


def test_tools(obj):
    """
    Check object to see if it has the correct members to be used in job configuration.
    """
    obj_cp = copy.deepcopy(obj)
    # Loops through all tools
    try:
        for tool in obj.keys():
            if tool == "default":
                # Check universal default
                curr_tool = obj[tool]
                try:
                    cond_action = curr_tool["destinationID"]
                except (KeyError, TypeError):
                    raise MalformedYMLException("Error getting default destinationID.")

                try:
                    cond_action = curr_tool["runner"]
                except (KeyError, TypeError):
                    raise MalformedYMLException("Error getting default runner.")
            else:
                curr_tool = obj[tool]
                # Loops through all conditions for the current tool
                for condition in curr_tool:
                    # Checks if the current condition has a type,
                    # and, from the type, checks for other parameters.
                    curr_cond = curr_tool[condition]
                    try:
                        try:
                            # Search for a type attribute
                            cond_type = curr_cond["type"]
                        except (KeyError, TypeError):
                            error = "Error getting " + str(condition)
                            error += " type for " + str(tool)
                            raise TypeError(error)

                        try:
                            # Search for a condition action
                            cond_action = curr_cond["action"]

                            if cond_action == "fail":
                                try:
                                    curr_cond["err_msg"]
                                except (KeyError, TypeError):
                                    error = "err_msg not set for " + str(condition)
                                    error += " in " + str(tool)
                                    log.debug(error)
                        except (KeyError, TypeError):
                            error = "Error getting " + str(condition)
                            error += " action in " + str(tool)
                            raise TypeError(error)

                        if cond_type != "default":
                            # Test the nice value if applicable
                            try:
                                curr_cond["nice"] = int(curr_cond["nice"])
                                if curr_cond["nice"] < -20 or curr_cond["nice"] > 20:
                                    error_info = "Nice value goes from -20 to 20: " + tool
                                    error_info += " " + condition + " nice:"
                                    error_info += str(curr_cond["nice"])
                                    log.debug(error_info)
                                    raise KeyError()
                            except KeyError:
                                error_resolve = "Invalid nice value. Setting "
                                error_resolve += tool + " " + condition + " nice to 0."
                                log.debug(error_resolve)
                                obj_cp[tool][condition]["nice"] = 0

                        if cond_type == "filesize" or cond_type == "records":
                            # Test for filesize/records specific members
                            try:
                                curr_cond["lbound"]
                            except (KeyError, TypeError):
                                error = "Error getting " + str(condition)
                                error += " lbound in " + str(tool)
                                raise TypeError(error)

                            try:
                                curr_cond["hbound"]
                            except (KeyError, TypeError):
                                error = "Error getting " + str(condition)
                                error += " hbound in " + str(tool)
                                raise TypeError(error)

                        elif cond_type == "parameter":
                            # Test for parameter specific members
                            try:
                                curr_cond["args"]
                            except KeyError:
                                error = "No args for " + str(condition)
                                error += " in " + str(tool)
                                raise TypeError(error)

                        elif cond_type == "default":
                            # No members specific to default, this is needed
                            # simply for type recognition
                            pass

                        else:
                            error = "Unrecognized " + str(condition) + " type "
                            error += str(cond_type) + " in " + str(tool)
                            raise TypeError(error)
                    except TypeError, e:
                        log.error(e)
                        error = "Deleting " + str(condition)
                        error += " in " + str(tool) + "..."
                        log.debug(error)
                        del obj_cp[tool][condition]
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


def map_tool_to_destination(job, app, tool, test=False,
    path="/config/tool_destinations.yml"):
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

        # Chooses behaviour based on tool

        # Get configuration from tool_options.yml
        try:
            behaviour = parse_yaml(path)
        except MalformedYMLException, e:
            raise JobMappingException(e)

        native_spec = {}
        try:
            # For each different condition for the tool that's running
            for key in behaviour[str(tool.old_id)]:
                condition = behaviour[str(tool.old_id)][key]

                if condition["type"] == "filesize":
                    hbound = str_to_bytes(condition["hbound"])
                    lbound = str_to_bytes(condition["lbound"])

                    if hbound == -1:
                        if lbound <= file_size:
                            native_spec = apply_magnitude(behaviour,
                                                          condition,
                                                          native_spec,
                                                          file_size,
                                                          test)
                    else:
                        if lbound <= file_size and file_size < hbound:
                            native_spec = apply_magnitude(behaviour,
                                                          condition,
                                                          native_spec,
                                                          file_size,
                                                          test)
                elif condition["type"] == "records":
                    hbound = str_to_bytes(condition["hbound"])
                    lbound = str_to_bytes(condition["lbound"])

                    if hbound == -1:
                        if lbound <= records:
                            native_spec = apply_magnitude(behaviour,
                                                          condition,
                                                          native_spec,
                                                          records,
                                                          test)
                    else:
                        if lbound <= records and records < hbound:
                            native_spec = apply_magnitude(behaviour,
                                                          condition,
                                                          native_spec,
                                                          records,
                                                          test)
                elif condition["type"] == "parameter":
                    # TODO: This accepts the condition if any parameter is correct,
                    #       we should probably change it to if all are correct

                    options = job.get_param_values(app)
                    for arg in condition["args"].keys():
                        if arg in options:
                            if condition["args"][arg] == options[arg]:
                                native_spec = apply_parameter(behaviour,
                                                              condition,
                                                              native_spec,
                                                              test)
                            else:
                                error = "Parameter value unequal -- " + str(tool.old_id)
                                error += " parameter:" + str(options[arg]) + " != "
                                error += "tool_options parameter:"
                                error += str(condition["args"][arg])
                                log.debug(error)
                elif condition["type"] == "default":
                    try:
                        cond_runner = condition["runner"]
                    except KeyError:
                        cond_runner = behaviour["default"]["runner"]

                    defaultCondition = {
                        "action": condition["action"],
                        "runner": cond_runner,
                    }

            # If nothing has been found, use the default option
            try:
                native_spec["action"]
                native_spec["runner"]
            except(KeyError, NameError, TypeError):
                raise KeyError()
        except KeyError:
            try:
                # Find default in job_options under the tool
                action = defaultCondition["action"]
                curr_runner = defaultCondition["runner"]
                dest = JobDestination(id="Dynamic " + str(tool.old_id) + " Default",
                                      runner=curr_runner,
                                      params={"nativeSpecification": action})
            except NameError:
                # Find default in job_options under default tool
                log.debug("Possible unconfigured tool: \"" + tool.old_id + "\"")
                try:
                    loc = behaviour["default"]["destinationID"]
                    dest = app.job_config.get_destination(loc)
                except KeyError:
                    # Only arrive here if parse_yaml fails
                    raise JobMappingException("No default in tool_options.yml")
        try:
            # If a default has been defined, ust it.
            return dest
        except NameError:
            # Else use the specified parameter for the destination.
            if test:
                logging.shutdown()
            return JobDestination(id="Dynamically_mapped " + tool.old_id,
                                  runner=native_spec["runner"],
                                  params={"nativeSpecification": native_spec["action"]})


def apply_magnitude(behaviour, condition, _native_spec, magnitude, test=False):
    """
    Preprocesses the native specification object for a condition of type
    filesize or records
    """
    if test:
        importer(test)

    action = str(condition["action"]).strip().lower()
    error_post = " on condition: " + condition["lbound"] + " < INPUT: "
    error_post += bytes_to_str(magnitude) + " < " + condition["hbound"]
    native_spec = ""

    if action == "fail":
        # TODO: This will fail even if there are nice values later
        #       on in tool_options.yml that are larger than this.
        #       This should be fixed to delay failing of jobs until
        #       we are certain it is the item to apply.

        # Print error message and exit
        # Check for custom error message
        try:
            error = condition["err_msg"].strip() + error_post
        except KeyError:
            error = "Error" + error_post

        raise JobMappingException(error)
    else:
        # Check to see if the current condition has bounds overlapping
        # with other conditions of the same type
        try:
            if _native_spec["type"] == condition["type"]:
                if(_native_spec["type"] != "parameter"):
                    error = "Malformed XML: overlapping bounds" + error_post
                    raise JobMappingException(error)

            # If the nice values are equal, precendence is given to the
            # earliest defined condition.
            if _native_spec["nice"] > condition["nice"]:
                try:
                    cond_runner = condition["runner"]
                except KeyError:
                    cond_runner = behaviour["default"]["runner"]

                native_spec = condition
                native_spec["runner"] = cond_runner
        except KeyError:
            # If _native_spec has no "type"/"nice" attr, this
            # probably means it's the empty starting _native_spec
            try:
                cond_runner = condition["runner"]
            except KeyError:
                cond_runner = behaviour["default"]["runner"]

            native_spec = condition
            native_spec["runner"] = cond_runner

    return native_spec


def apply_parameter(behaviour, condition, _native_spec, test=False):
    """
    Preprocesses the native specification object for a condition of type
    parameter
    """
    if test:
        importer(test)

    native_spec = ""
    error = "Unexpeted error."

    try:
        # Raise errors for no nice values
        try:
            _native_spec["nice"]
        except KeyError:
            error = "Nice value not set for condition:"
            error += str(_native_spec)
            raise KeyError(error)

        try:
            condition["nice"]
        except KeyError:
            error = "Nice value not set for condition:"
            error += str(condition)
            raise KeyError(error)

        # If the nice values are equal, precendence is given to the
        # earliest defined condition.
        if _native_spec["nice"] > condition["nice"]:
            if condition["action"] == "fail":
                # TODO: This will fail even if there are nice values later
                #       on in tool_options.yml that are larger than this.
                #       This should be fixed to delay failing of jobs until
                #       we are certain it is the item to apply.
                error_post = " on args: " + str(condition["args"])

                try:
                    error = condition["err_msg"].strip() + error_post
                except KeyError:
                    error = "Error" + error_post

                raise JobMappingException(error)
            else:
                try:
                    cond_runner = condition["runner"]
                except KeyError:
                    cond_runner = behaviour["default"]["runner"]

                native_spec = condition
                native_spec["runner"] = cond_runner
    except KeyError, x:
        log.debug(x)

    return native_spec
