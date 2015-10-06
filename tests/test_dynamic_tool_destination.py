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
'''
Created on June 23rd, 2015

@author: Daniel Bouchard
'''
import logging
import os
import re
import sys
sys.path.append("")
import unittest
import mockGalaxy as mg
import ymltests as yt
import dynamic_tool_destination.DynamicToolDestination as dt

from dynamic_tool_destination.DynamicToolDestination import map_tool_to_destination
from dynamic_tool_destination.DynamicToolDestination import apply_magnitude
from dynamic_tool_destination.DynamicToolDestination import apply_parameter
from testfixtures import log_capture


theApp = mg.App( "waffles_default", "test_spec")

#======================Jobs====================================
zeroJob = mg.Job()

emptyJob = mg.Job()
emptyJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test.empty"), "txt", 14)) )

failJob = mg.Job()
failJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test1.full"), "txt", 15)) )

msfileJob = mg.Job()
msfileJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/not_here.full"), "txt", 15)) )

notfileinpJob = mg.Job()
msfileJob.add_input_dataset( mg.InputDataset("input1", mg.NotAFile() ) )

runJob = mg.Job()
runJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test3.full"), "txt", 15)) )

vfJob = mg.Job()
vfJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test3.full"), "txt", 15)) )
vfJob.set_param_value( "mlst_or_genedb", {"vfdb_in": "-bact"} )

paramJob = mg.Job()
paramJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test3.full"), "txt", 15)) )
paramJob.set_param_value( "careful", True )

argNotFoundJob = mg.Job()
argNotFoundJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test3.full"), "txt", 15)) )
argNotFoundJob.set_param_value( "careful", False )

notvfJob = mg.Job()
notvfJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test3.full"), "txt", 15)) )
notvfJob.set_param_value( "mlst_or_genedb", {"vfdb_in": "-not_here"} )

dbJob = mg.Job()
dbJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test.fasta"), "fasta", 10)) )

dbcountJob = mg.Job()
dbcountJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test.fasta"), "fasta", None)) )

vfdbJob = mg.Job()
vfdbJob.add_input_dataset( mg.InputDataset("input1", mg.Dataset( (os.getcwd() + "/tests/data/test.fasta"), "fasta", 6)) )
vfdbJob.set_param_value( "mlst_or_genedb", {"vfdb_in": "-bact"} )

#======================Tools===================================
vanillaTool = mg.Tool( 'test' )

unTool = mg.Tool( 'unregistered' )

overlapTool = mg.Tool( 'test_overlap' )

defaultTool = mg.Tool( 'test_tooldefault' )

dbTool = mg.Tool( 'test_db' )
dbinfTool = mg.Tool( 'test_db_high' )

nomsgTool = mg.Tool( 'test_no_errmsg' )

paramTool = mg.Tool( 'test_parameter' )

customRunnerTool = mg.Tool( 'test_custom_runner' )

vfdbTool = mg.Tool( 'test_db' )
vfdbTool.add_tool_dependency( mg.ToolDependency("vfdb", os.getcwd() + "/tests") )

#=======================YML file================================
path = "/tests/data/tool_destination.yml"
err_path = "/tests/data/no_errmsg.yml"
broken_runner_path = "/tests/data/runner_fail.yml"
broken_default_dest_path = "/tests/data/dest_fail.yml"

#======================Test Variables=========================
value = 1
valueK = value * 1024
valueM = valueK * 1024
valueG = valueM * 1024
valueT = valueG * 1024
valueP = valueT * 1024
valueE = valueP * 1024
valueZ = valueE * 1024
valueY = valueZ * 1024


class TestDynamicToolDestination(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        logger = logging.getLogger()

    #=======================map_tool_to_destination()================================
    @log_capture()
    def test_brokenRunnerYML(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, runJob, theApp, vanillaTool, True, broken_runner_path)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting default runner.')
        )

    @log_capture()
    def test_brokenDestYML(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, runJob, theApp, vanillaTool, True, broken_default_dest_path)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting default destinationID.')
        )

    @log_capture()
    def test_custom_runner(self, l):
        job = map_tool_to_destination( runJob, theApp, customRunnerTool, True, path )
        self.assertEquals( job.id, 'Dynamically_mapped test_custom_runner' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 4 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'custom_runner' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
        )

    @log_capture()
    def test_filesize_empty(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, emptyJob, theApp, vanillaTool, True, path )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test.empty'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 0.00 B'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
        )

    @log_capture()
    def test_filesize_zero(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, zeroJob, theApp, vanillaTool, True, path )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 0.00 B'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
        )

    @log_capture()
    def test_filesize_fail(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, failJob, theApp, vanillaTool, True, path )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test1.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 293.00 B'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
        )

    @log_capture()
    def test_fnf(self, l):
        self.assertRaises( mg.JobMappingException, map_tool_to_destination, msfileJob, theApp, vanillaTool, True, path )
        if sys.version_info < (2, 7):
            self.assertTrue(re.match( r".*Total size: 0\.00 B", str(l.records[1]) ))
            self.assertTrue(re.match( r".*Total amount of records: 0", str(l.records[2]) ))
        else:
            self.assertRegexpMatches( str(l.records[1]), r".*Total size: 0\.00 B")
            self.assertRegexpMatches( str(l.records[2]), r".*Total amount of records: 0")

    @log_capture()
    def test_filesize_run(self, l):
        job = map_tool_to_destination( runJob, theApp, vanillaTool, True, path )
        self.assertEquals( job.id, 'Dynamically_mapped test' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 4 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0')
        )

    @log_capture()
    def test_default_tool(self, l):
        job = map_tool_to_destination( runJob, theApp, defaultTool, True, path )
        self.assertEquals( job.id, 'Dynamic test_tooldefault Default' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 16 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0')
        )

    @log_capture()
    def test_parameter_tool(self, l):
        job = map_tool_to_destination( paramJob, theApp, paramTool, True, path )
        self.assertEquals( job.id, 'Dynamic test_parameter Default' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 16 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', "'Nice value not set for condition:{}'")
        )

    @log_capture()
    def test_parameter_arg_not_found(self, l):
        job = map_tool_to_destination( argNotFoundJob, theApp, paramTool, True, path )
        self.assertEquals( job.id, 'Dynamic test_parameter Default' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 16 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG',
             'Parameter value unequal -- test_parameter parameter:False != tool_options parameter:True')
        )

    @log_capture()
    def test_tool_not_found(self, l):
        job = map_tool_to_destination( runJob, theApp, unTool, True, path )
        self.assertEquals( job.id, 'waffles_default' )
        self.assertEquals( job.nativeSpec, '-q test.q' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG',
             'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Possible unconfigured tool: "unregistered"')
        )

    @log_capture()
    def test_fasta(self, l):
        job = map_tool_to_destination( dbJob, theApp, dbTool, True, path )
        self.assertEquals( job.id, 'Dynamically_mapped test_db' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 4 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test.fasta'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 0.00 B'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 10'),
        )

    @log_capture()
    def test_fasta_count(self, l):
        job = map_tool_to_destination( dbcountJob, theApp, dbTool, True, path )
        self.assertEquals( job.id, 'Dynamically_mapped test_db' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 4 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test.fasta'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 0.00 B'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 6'),
        )

    @log_capture()
    def test_vf(self, l):
        job = map_tool_to_destination( vfJob, theApp, vfdbTool, True, path )
        self.assertEquals( job.id, 'Dynamically_mapped test_db' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 4 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: ' + os.getcwd() + '/tests/vfdb/?bact.test'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 4'),
        )

    @log_capture()
    def test_vf_not_found(self, l):
        job = map_tool_to_destination( notvfJob, theApp, vfdbTool, True, path )
        self.assertEquals( job.id, 'Dynamically_mapped test_db' )
        self.assertEquals( job.nativeSpec, '-q test.q -pe galaxy 4 -l h_vmem=2G' )
        self.assertEquals( job.runner, 'drmaa' )

        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'INFO', 'No virulence factors database'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG',
             'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
        )

    #=======================apply_magnitude()================================
    @log_capture()
    def test_overlap_options(self, l):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "filesize",
            'nice': 0,
            "lbound": "0",
            "hbound": "100",
            "action": "things"
        }
        native_spec = {
            "type": "filesize",
            'nice': 0,
            "action": "things"
        }
        self.assertRaises(mg.JobMappingException, apply_magnitude, behaviour, condition, native_spec, 0, True )
        l.check()

    @log_capture()
    def test_nice_comparison(self, l):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "filesize",
            'nice': 0,
            "lbound": "0",
            "hbound": "100",
            "action": "things"
        }
        native_spec = {
            "type": "records",
            'nice': 1,
            "action": "things"
        }
        self.assertEquals(apply_magnitude(behaviour, condition, native_spec, 0, True), condition)
        l.check()

    @log_capture()
    def test_no_err_msg(self, l):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "filesize",
            'nice': 0,
            "lbound": "0",
            "hbound": "100",
            "action": "fail"
        }
        native_spec = {
            "type": "records",
            'nice': 1,
            "action": "things"
        }
        self.assertRaises(mg.JobMappingException, apply_magnitude, behaviour, condition, native_spec, 0, True )

    #=======================apply_parameter()================================
    @log_capture()
    def test_normal_parameter(self, l):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "parameter",
            "nice": 0,
            "args": {"careful": True},
            "err_msg": "Failure",
            "action": "things"
        }
        native_spec = {
            "type": "records",
            'nice': 1,
            "action": "things"
        }
        self.assertEquals(apply_parameter(behaviour, condition, native_spec, True), condition)
        l.check()

    @log_capture()
    def test_fail_parameter(self, l):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "parameter",
            "nice": 0,
            "args": {"careful": True},
            "err_msg": "Failure",
            "action": "fail"
        }
        native_spec = {
            "type": "records",
            'nice': 1,
            "action": "things"
        }
        self.assertRaises(mg.JobMappingException, apply_parameter, behaviour, condition, native_spec, True)

    @log_capture()
    def test_fail_parameter_no_msg(self, l):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "parameter",
            "nice": 0,
            "args": {"careful": True},
            "action": "fail"
        }
        native_spec = {
            "type": "records",
            'nice': 1,
            "action": "things"
        }
        self.assertRaises(mg.JobMappingException, apply_parameter, behaviour, condition, native_spec, True)

    def test_no_spec_nice_value(self):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "parameter",
            "nice": 0,
            "args": {"careful": True},
            "action": "fail"
        }
        native_spec = {
            "type": "default",
            "action": "things"
        }
        self.assertEquals(apply_parameter(behaviour, condition, native_spec, True), "")

    def test_no_cond_nice_value(self):
        behaviour = {"default": {"runner": "drmaa"}}
        condition = {
            "type": "parameter",
            "args": {"careful": True},
            "action": "fail"
        }
        native_spec = {
            "type": "default",
            "nice": 0,
            "action": "things"
        }
        self.assertEquals(apply_parameter(behaviour, condition, native_spec, True), "")

#================================Invalid yaml files==============================
    @log_capture()
    def test_no_file(self, l):
        self.assertRaises(IOError, dt.parse_yaml, path="")
        l.check()

    @log_capture()
    def test_bad_nice(self, l):
        dt.parse_yaml(path=yt.ivYMLTest11, test=True)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG',
             'Nice value goes from -20 to 20: spades condition1 nice:-21'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG',
             'Invalid nice value. Setting spades condition1 nice to 0.')
        )

    @log_capture()
    def test_tool_extra_attr(self, l):
        dt.parse_yaml(path=yt.ivYMLTest1, test=True)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting age type for spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting age in spades...')
        )

    @log_capture()
    def test_empty_file(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest2, test=True), None)
        l.check(('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Illegal object: None'))

    @log_capture()
    def test_no_tool_name(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest3, test=True), yt.iv3dict)
        for log_item in l.records:
            if('Error getting lbound type for condition1' == str(log_item.msg) or
               'Error getting type type for condition1' == str(log_item.msg) or
               'Error getting hbound type for condition1' == str(log_item.msg) or
               'Error getting action type for condition1' == str(log_item.msg) or
               'Error getting nice type for condition1' == str(log_item.msg) or
               'Deleting nice in condition1...' == str(log_item.msg) or
               'Deleting action in condition1...' == str(log_item.msg) or
               'Deleting hbound in condition1...' == str(log_item.msg) or
               'Deleting lbound in condition1...' == str(log_item.msg) or
               'Deleting type in condition1...' == str(log_item.msg)):
                pass
            else:
                self.fail("Couldn't find '" + str(log_item.msg) + "' in log.")

    @log_capture()
    def test_no_cond_type(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest4, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting condition1 type for spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_cond_lbound(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest51, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting condition1 lbound in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_cond_hbound(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest52, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting condition1 hbound in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_cond_param(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest53, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting condition1 action in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_bad_cond_type(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest6, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Unrecognized condition1 type iencs in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_err_msg(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest91, test=True), yt.iv91dict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'err_msg not set for condition1 in spades'),
            ('dynamic_tool_destination.DynamicToolDestination',
             'DEBUG',
             'Invalid nice value. Setting spades condition1 nice to 0.')
        )

    @log_capture()
    def test_default_fail_no_err_msg(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest92, test=True), yt.iv92dict)
        l.check(('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'err_msg not set for condition1 in spades'))

    @log_capture()
    def test_default_fail_no_param(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest10, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting condition1 action in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_default_dest(self, l):
        self.assertRaises(dt.MalformedYMLException, dt.parse_yaml, path=yt.ivYMLTest7, test=True)
        l.check(('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting default destinationID.'))

    @log_capture()
    def test_no_default_runner(self, l):
        self.assertRaises(dt.MalformedYMLException, dt.parse_yaml, path=yt.ivYMLTest8, test=True)
        l.check(('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting default runner.'))

    @log_capture()
    def test_parameter_no_err_msg(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest12, test=True), yt.iv12dict)
        l.check(('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'err_msg not set for condition1 in spades'))

    @log_capture()
    def test_parameter_no_args(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest131, test=True), yt.iv13dict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'No args for condition1 in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_parameter_no_param(self, l):
        self.assertEquals(dt.parse_yaml(path=yt.ivYMLTest132, test=True), yt.iv13dict)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'ERROR', 'Error getting condition1 action in spades'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Deleting condition1 in spades...')
        )

#================================Valid yaml files==============================
    @log_capture()
    def test_parse_valid_yml(self, l):
        self.assertEqual(dt.parse_yaml(yt.vYMLTest1, test=True), yt.vdictTest1_yml)
        self.assertEqual(dt.parse_yaml(yt.vYMLTest2, test=True), yt.vdictTest2_yml)
        self.assertEqual(dt.parse_yaml(yt.vYMLTest3, test=True), yt.vdictTest3_yml)
        self.assertEqual(dt.parse_yaml(yt.vYMLTest4, test=True), yt.vdictTest4_yml)
        l.check()

#================================Testing str_to_bytes==========================
    def test_str_to_bytes_invalid(self):
        self.assertRaises(dt.MalformedYMLException, dt.str_to_bytes, "1d")
        self.assertRaises(dt.MalformedYMLException, dt.str_to_bytes, "1 d")

    def test_str_to_bytes_valid(self):
        self.assertEqual(dt.str_to_bytes("-1"), -1)
        self.assertEqual(dt.str_to_bytes( "1" ), value)
        self.assertEqual(dt.str_to_bytes( 156 ), 156)
        self.assertEqual(dt.str_to_bytes( "1 B" ), value)
        self.assertEqual(dt.str_to_bytes( "1 KB" ), valueK)
        self.assertEqual(dt.str_to_bytes( "1 MB" ), valueM)
        self.assertEqual(dt.str_to_bytes( "1 gB" ), valueG)
        self.assertEqual(dt.str_to_bytes( "1 Tb" ), valueT)
        self.assertEqual(dt.str_to_bytes( "1 pb" ), valueP)
        self.assertEqual(dt.str_to_bytes( "1 EB" ), valueE)
        self.assertEqual(dt.str_to_bytes( "1 ZB" ), valueZ)
        self.assertEqual(dt.str_to_bytes( "1 YB" ), valueY)

#==============================Testing bytes_to_str=============================
    @log_capture()
    def test_bytes_to_str_invalid(self, l):
        testValue = ""
        self.assertRaises( ValueError, dt.bytes_to_str, testValue )
        testValue = "5564fads"
        self.assertRaises( ValueError, dt.bytes_to_str, testValue )
        testValue = "45.0.1"
        self.assertRaises( ValueError, dt.bytes_to_str, testValue )
        self.assertRaises( ValueError, dt.bytes_to_str, "1 024" )

    def test_bytes_to_str_valid(self):
        self.assertEqual(dt.bytes_to_str(-1), "Infinity")
        self.assertEqual(dt.bytes_to_str( value), "1.00 B")
        self.assertEqual(dt.bytes_to_str( valueK), "1.00 KB")
        self.assertEqual(dt.bytes_to_str( valueM), "1.00 MB")
        self.assertEqual(dt.bytes_to_str( valueG), "1.00 GB")
        self.assertEqual(dt.bytes_to_str( valueT ), "1.00 TB")
        self.assertEqual(dt.bytes_to_str( valueP ), "1.00 PB")
        self.assertEqual(dt.bytes_to_str( valueE ), "1.00 EB")
        self.assertEqual(dt.bytes_to_str( valueZ ), "1.00 ZB")
        self.assertEqual(dt.bytes_to_str( valueY ), "1.00 YB")

        self.assertEqual(dt.bytes_to_str( 10, "B" ), "10.00 B")
        self.assertEqual(dt.bytes_to_str( 1000000, "KB" ), "976.56 KB")
        self.assertEqual(dt.bytes_to_str( 1000000000, "MB" ), "953.67 MB")
        self.assertEqual(dt.bytes_to_str( 1000000000000, "GB" ), "931.32 GB")
        self.assertEqual(dt.bytes_to_str( 1000000000000000, "TB" ), "909.49 TB")
        self.assertEqual(dt.bytes_to_str( 1000000000000000000, "PB" ), "888.18 PB")
        self.assertEqual(dt.bytes_to_str( 1000000000000000000000, "EB" ), "867.36 EB")
        self.assertEqual(dt.bytes_to_str( 1000000000000000000000000, "ZB" ), "847.03 ZB")

        self.assertEqual(dt.bytes_to_str( value, "KB" ), "1.00 B")
        self.assertEqual(dt.bytes_to_str( valueK, "MB" ), "1.00 KB")
        self.assertEqual(dt.bytes_to_str( valueM, "GB" ), "1.00 MB")
        self.assertEqual(dt.bytes_to_str( valueG, "TB" ), "1.00 GB")
        self.assertEqual(dt.bytes_to_str( valueT, "PB" ), "1.00 TB")
        self.assertEqual(dt.bytes_to_str( valueP, "EB" ), "1.00 PB")
        self.assertEqual(dt.bytes_to_str( valueE, "ZB" ), "1.00 EB")
        self.assertEqual(dt.bytes_to_str( valueZ, "YB" ), "1.00 ZB")

        self.assertEqual(dt.bytes_to_str( "1" ), "1.00 B")
        self.assertEqual(dt.bytes_to_str( "\t\t1000000" ), "976.56 KB")
        self.assertEqual(dt.bytes_to_str( "1000000000\n" ), "953.67 MB")
        self.assertEqual(dt.bytes_to_str( 1024, "fda" ), "1.00 KB")

if __name__ == '__main__':
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestDynamicToolDestination)
    #ret = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    #print(ret)
    #sys.exit(ret)
