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
Created on June 1st

@author: Daniel Bouchard

Notes: run with cmd=python -m testing.helperTest from galaxy_smart_submission
"""
import sys
sys.path.append("")
import dynamic_tool_destination.helperMethods as hm
import ymltests as yt
import unittest

import logging
from testfixtures import log_capture

value = 1
valueK = value * 1024
valueM = valueK * 1024
valueG = valueM * 1024
valueT = valueG * 1024
valueP = valueT * 1024
valueE = valueP * 1024
valueZ = valueE * 1024
valueY = valueZ * 1024

class TestHelperMethods(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        logger = logging.getLogger()

#================================Invalid yaml files==============================
    @log_capture()
    def test_no_file(self, l):
        self.assertRaises(IOError, hm.parse_yaml, path="")
        l.check()

    @log_capture()
    def test_bad_nice(self, l):
        hm.parse_yaml(path=yt.ivYMLTest11, test=True)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'DEBUG',
             'Nice value goes from -20 to 20: spades condition1 nice:-21'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG',
             'Invalid nice value. Setting spades condition1 nice to 0.')
        )

    @log_capture()
    def test_tool_extra_attr(self, l):
        hm.parse_yaml(path=yt.ivYMLTest1, test=True)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting age type for spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting age in spades...')
        )

    @log_capture()
    def test_empty_file(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest2, test=True), None)
        l.check(('dynamic_tool_destination.helperMethods', 'DEBUG', 'Illegal object: None'))

    @log_capture()
    def test_no_tool_name(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest3, test=True), yt.iv3dict)
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
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest4, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting condition1 type for spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_cond_lbound(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest51, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting condition1 lbound in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_cond_hbound(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest52, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting condition1 hbound in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_cond_param(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest53, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting condition1 action in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_bad_cond_type(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest6, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Unrecognized condition1 type iencs in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_err_msg(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest91, test=True), yt.iv91dict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'err_msg not set for condition1 in spades'),
            ('dynamic_tool_destination.helperMethods',
             'DEBUG',
             'Invalid nice value. Setting spades condition1 nice to 0.')
        )

    @log_capture()
    def test_default_fail_no_err_msg(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest92, test=True), yt.iv92dict)
        l.check(('dynamic_tool_destination.helperMethods', 'DEBUG', 'err_msg not set for condition1 in spades'))

    @log_capture()
    def test_default_fail_no_param(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest10, test=True), yt.ivDict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting condition1 action in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_no_default_dest(self, l):
        self.assertRaises(hm.MalformedYMLException, hm.parse_yaml, path=yt.ivYMLTest7, test=True)
        l.check(('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting default destinationID.'))

    @log_capture()
    def test_no_default_runner(self, l):
        self.assertRaises(hm.MalformedYMLException, hm.parse_yaml, path=yt.ivYMLTest8, test=True)
        l.check(('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting default runner.'))

    @log_capture()
    def test_parameter_no_err_msg(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest12, test=True), yt.iv12dict)
        l.check(('dynamic_tool_destination.helperMethods', 'DEBUG', 'err_msg not set for condition1 in spades'))

    @log_capture()
    def test_parameter_no_args(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest131, test=True), yt.iv13dict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'No args for condition1 in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

    @log_capture()
    def test_parameter_no_param(self, l):
        self.assertEquals(hm.parse_yaml(path=yt.ivYMLTest132, test=True), yt.iv13dict)
        l.check(
            ('dynamic_tool_destination.helperMethods', 'ERROR', 'Error getting condition1 action in spades'),
            ('dynamic_tool_destination.helperMethods', 'DEBUG', 'Deleting condition1 in spades...')
        )

#================================Valid yaml files==============================
    @log_capture()
    def test_parse_valid_yml(self, l):
        self.assertEqual(hm.parse_yaml(yt.vYMLTest1, test=True), yt.vdictTest1_yml)
        self.assertEqual(hm.parse_yaml(yt.vYMLTest2, test=True), yt.vdictTest2_yml)
        self.assertEqual(hm.parse_yaml(yt.vYMLTest3, test=True), yt.vdictTest3_yml)
        self.assertEqual(hm.parse_yaml(yt.vYMLTest4, test=True), yt.vdictTest4_yml)
        l.check()

#================================Testing str_to_bytes==========================
    def test_str_to_bytes_invalid(self):
        self.assertRaises(hm.MalformedYMLException, hm.str_to_bytes, "1d")
        self.assertRaises(hm.MalformedYMLException, hm.str_to_bytes, "1 d")
        
    def test_str_to_bytes_valid(self):
        self.assertEqual(hm.str_to_bytes("-1"), -1)
        self.assertEqual(hm.str_to_bytes( "1" ), value)
        self.assertEqual(hm.str_to_bytes( 156 ), 156)
        self.assertEqual(hm.str_to_bytes( "1 B" ), value)
        self.assertEqual(hm.str_to_bytes( "1 KB" ), valueK)
        self.assertEqual(hm.str_to_bytes( "1 MB" ), valueM)
        self.assertEqual(hm.str_to_bytes( "1 gB" ), valueG)
        self.assertEqual(hm.str_to_bytes( "1 Tb" ), valueT)
        self.assertEqual(hm.str_to_bytes( "1 pb" ), valueP)
        self.assertEqual(hm.str_to_bytes( "1 EB" ), valueE)
        self.assertEqual(hm.str_to_bytes( "1 ZB" ), valueZ)
        self.assertEqual(hm.str_to_bytes( "1 YB" ), valueY)

#==============================Testing bytes_to_str=============================
    @log_capture()
    def test_bytes_to_str_invalid(self, l):
        testValue = ""
        self.assertRaises( ValueError, hm.bytes_to_str, testValue )
        testValue = "5564fads"
        self.assertRaises( ValueError, hm.bytes_to_str, testValue )
        testValue = "45.0.1"
        self.assertRaises( ValueError, hm.bytes_to_str, testValue )
        self.assertRaises( ValueError, hm.bytes_to_str, "1 024" )
        
    def test_bytes_to_str_valid(self):
        self.assertEqual(hm.bytes_to_str(-1), "Infinity")
        self.assertEqual(hm.bytes_to_str( value), "1.00 B")
        self.assertEqual(hm.bytes_to_str( valueK), "1.00 KB")
        self.assertEqual(hm.bytes_to_str( valueM), "1.00 MB")
        self.assertEqual(hm.bytes_to_str( valueG), "1.00 GB")
        self.assertEqual(hm.bytes_to_str( valueT ), "1.00 TB")
        self.assertEqual(hm.bytes_to_str( valueP ), "1.00 PB")
        self.assertEqual(hm.bytes_to_str( valueE ), "1.00 EB")
        self.assertEqual(hm.bytes_to_str( valueZ ), "1.00 ZB")
        self.assertEqual(hm.bytes_to_str( valueY ), "1.00 YB")
        
        self.assertEqual(hm.bytes_to_str( 10, "B" ), "10.00 B")
        self.assertEqual(hm.bytes_to_str( 1000000, "KB" ), "976.56 KB")
        self.assertEqual(hm.bytes_to_str( 1000000000, "MB" ), "953.67 MB")
        self.assertEqual(hm.bytes_to_str( 1000000000000, "GB" ), "931.32 GB")
        self.assertEqual(hm.bytes_to_str( 1000000000000000, "TB" ), "909.49 TB")
        self.assertEqual(hm.bytes_to_str( 1000000000000000000, "PB" ), "888.18 PB")
        self.assertEqual(hm.bytes_to_str( 1000000000000000000000, "EB" ), "867.36 EB")
        self.assertEqual(hm.bytes_to_str( 1000000000000000000000000, "ZB" ), "847.03 ZB")
        
        self.assertEqual(hm.bytes_to_str( value, "KB" ), "1.00 B")
        self.assertEqual(hm.bytes_to_str( valueK, "MB" ), "1.00 KB")
        self.assertEqual(hm.bytes_to_str( valueM, "GB" ), "1.00 MB")
        self.assertEqual(hm.bytes_to_str( valueG, "TB" ), "1.00 GB")
        self.assertEqual(hm.bytes_to_str( valueT, "PB" ), "1.00 TB")
        self.assertEqual(hm.bytes_to_str( valueP, "EB" ), "1.00 PB")
        self.assertEqual(hm.bytes_to_str( valueE, "ZB" ), "1.00 EB")
        self.assertEqual(hm.bytes_to_str( valueZ, "YB" ), "1.00 ZB")
        
        self.assertEqual(hm.bytes_to_str( "1" ), "1.00 B")
        self.assertEqual(hm.bytes_to_str( "\t\t1000000" ), "976.56 KB")
        self.assertEqual(hm.bytes_to_str( "1000000000\n" ), "953.67 MB")
        self.assertEqual(hm.bytes_to_str( 1024, "fda" ), "1.00 KB")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHelperMethods)
    ret = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    print(ret)
    sys.exit(ret)
