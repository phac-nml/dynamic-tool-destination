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
Created on June 1st, 2015

@author: Daniel Bouchard
"""
from yaml import load
import copy
import logging
import os
import string
import sys

# log to galaxy's logger
log = logging.getLogger(__name__)


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
