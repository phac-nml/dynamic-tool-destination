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

class TestDynamicToolDestination(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger()

    #=======================map_tool_to_destination()================================
    @log_capture()
    def test_brokenRunnerYML(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, runJob, theApp, vanillaTool, True, broken_runner_path)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting default runner.')
        )

    @log_capture()
    def test_brokenDestYML(self, l):
        self.assertRaises(mg.JobMappingException, map_tool_to_destination, runJob, theApp, vanillaTool, True, broken_default_dest_path)
        l.check(
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Loading file: input1' + os.getcwd() + '/tests/data/test3.full'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total size: 3.23 KB'),
            ('dynamic_tool_destination.DynamicToolDestination', 'DEBUG', 'Total amount of records: 0'),
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting default destinationID.')
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

if __name__ == '__main__':
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestDynamicToolDestination)
    #ret = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    #print(ret)
    #sys.exit(ret)
