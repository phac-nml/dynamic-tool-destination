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
#=============================================Valid XML===================================================
# One job, one condition
vYMLTest1 = """
    spades:
      rules:
        - rule_type: file_size
          nice_value: 0
          lower_bound: 0
          upper_bound: 100000000
          destination: things
    default_destination: waffles_default
"""

vdictTest1_yml = {
    "spades": {
        "rules": [
            {
                "rule_type": "file_size",
                "nice_value": 0,
                "lower_bound": 0,
                "upper_bound": 100000000,
                "destination": "things"
            },
        ]
    },
    'default_destination': "waffles_default"
}

# Multiple jobs, multiple conditions
vYMLTest2 ='''
    spades:
      default_destination: waffles_default
    smalt:
      rules:
        - rule_type: file_size
          nice_value: 0
          lower_bound: 0
          upper_bound: 100000000
          fail_message: Too few reads for smalt to work
          destination: fail
        - rule_type: file_size
          nice_value: 0
          lower_bound: 100000000
          upper_bound: Infinity
          fail_message: Too few reads for smalt to work
          destination: fail
    default_destination: waffles_low
'''

vdictTest2_yml = {
    "spades": {
        "default_destination": "waffles_default"
    },
    "smalt": {
        "rules": [
            {
              "rule_type": "file_size",
              'nice_value': 0,
              "lower_bound": 0,
              "upper_bound": 100000000,
              "fail_message": "Too few reads for smalt to work",
              "destination": "fail"
            },{
              "rule_type": "file_size",
              'nice_value': 0,
              "lower_bound": 100000000,
              "upper_bound": "Infinity",
              "fail_message": "Too few reads for smalt to work",
              "destination": "fail"
            }
        ]
    },
    'default_destination': "waffles_low"
}

# Condition with extra attribute
vYMLTest3 = '''
    spades:
      rules:
        - rule_type: file_size
          nice_value: 0
          hax: 1337
          lower_bound: 0
          upper_bound: 100000000
          fail_message: Whats hax
          destination: fail
    default_destination: waffles_default
'''

vdictTest3_yml = {
    "spades": {
        "rules": [
            {
                "rule_type": "file_size",
                'nice_value': 0,
                "hax": 1337,
                "lower_bound": 0,
                "upper_bound": 100000000,
                "fail_message": "Whats hax",
                "destination": "fail"
            }
        ]
    },
    'default_destination': "waffles_low"
}

# Arguments type
vYMLTest4 = """
    spades:
      rules:
        - rule_type: arguments
          nice_value: 0
          arguments:
            - careful: true
          fail_message: Failure
          destination: fail
    default_destination: waffles_default
"""

vdictTest4_yml = {
    "spades": {
        "rules": [
            {
                "rule_type": "parameter",
                'nice_value': 0,
                "arguments": {
                    "careful": True,
                },
                "fail_message": "Failure",
                "destination": "fail"
            }
        ]
    },
    'default_destination': "waffles_default"
}

#=====================================================Invalid XML tests==========================================================

# Job with extra attribute
ivYMLTest1 = '''
    spades:
      rules:
        age: 5
          - rule_type: file_size
            nice_value: 0
            lower_bound: 0
            upper_bound: 100000000
            fail_message: Too few reads for spades to work
            destination: fail
    default_destination: waffles_default
'''

# Empty file
ivYMLTest2 = ""

# Job without name
ivYMLTest3 = '''
    rules:
      - rule_type: file_size
        nice_value: 0
        upper_bound: 100
        lower_bound: 0
        destination: fail
    default_destination: waffles_default
'''

iv3dict = {
    'default_destination': "waffles_default",
    'rules': {}
}

# Condition missing type
ivYMLTest4 = '''
    spades:
      rules:
        - nice_value: 0
          lower_bound: 0
          upper_bound: 0
          fail_message: No type...
          destination: fail
    default_destination: waffles_default
'''

# Condition missing attribute
ivYMLTest51 = '''
    spades:
      rules:
        - rule_type: file_size
          nice_value: 0
          upper_bound: 0
          fail_message: No type...
          destination: fail
    default_destination: waffles_default
'''

# Condition missing attribute
ivYMLTest52 = '''
    spades:
      rules:
        - rule_type: file_size
          nice_value: 0
          lower_bound: 0
          fail_message: No type...
          destination: fail
    default_destination: waffles_default
'''

# Condition missing attribute
ivYMLTest53 = '''
    spades:
      rules:
        - rule_type: file_size
          nice_value: 0
          lower_bound: 0
          upper_bound: 0
          fail_message: No type...
    default_destination: waffles_default
'''

# Condition unknown type
ivYMLTest6 = '''
    spades:
      rules:
        - rule_type: iencs
          nice_value: 0
          lower_bound: 0
          upper_bound: 0
          fail_message: No type...
          destination: fail
    default_destination: waffles_default
'''

ivDict = {
    'default_destination': "waffles_default",
    'spades': {
        'rules': [
            {
                'fail_message': 'No type...',
                'nice_value': 0,
                'upper_bound': 0,
                'lower_bound': 0,
                'destination': 'fail',
                'rule_type': 'iencs'
            }
        ]
    }
}

# Tool condition fail no fail_message
ivYMLTest91 = '''
    spades:
      rules:
        - rule_type: file_size
          lower_bound: 0
          upper_bound: 0
          destination: fail
    default_destination: waffles_default
'''

iv91dict = {
    'spades': {
        'rules': [
            {
                'lower_bound': 0,
                'nice_value': 0,
                'rule_type': 'file_size',
                'upper_bound': 0,
                'destination': 'fail'
            }
        ]
    },
    'default_destination': "waffles_default"
}

# Tool default fail no fail_message
ivYMLTest92 = '''
    spades:
      rules:
        - rule_type: default
          lower_bound: 0
          upper_bound: 0
          destination: fail
    default_destination: waffles_default
'''

iv92dict = {
    'spades': {
        'rules': [
            {
                'lower_bound': '0',
                'rule_type': 'default',
                'upper_bound': '0',
                'destination': 'fail'
            }
        ]
    },
    'default_destination': "waffles_default"
}

# Tool default fail no destination
ivYMLTest10 = '''
    spades:
      rules:
        - rule_type: default
          lower_bound: 0
          upper_bound: 0
    default_destination: default
'''

ivYMLTest11 = '''
    spades:
      rules:
        - rule_type: file_size
          nice_value: -21
          lower_bound: 1 KB
          upper_bound: Infinity
          destination: waffles_low
      default_destination: waffles_low
    default_destination: waffles_default
'''

# Arguments fail no fail_message
ivYMLTest12 = """
    spades:
      rules:
        - rule_type: arguments
          nice_value: 0
          arguments:
            - careful: true
          destination: fail
    default_destination: waffles_default
"""

iv12dict = {
    "spades": {
        "rules": [
            {
                "rule_type": "arguments",
                'nice_value': 0,
                "arguments": {
                    "careful": True,
                },
                "destination": "fail"
            }
        ]
    },
    'default_destination': "waffles_default"
}

# Arguments fail no arguments
ivYMLTest131 = """
    spades:
      rules:
        - rule_type: arguments
          nice_value: 0
          fail_message: Something went wrong
          destination: fail
    default_destination: waffles_default
"""

# Arguments fail no destination
ivYMLTest132 = """
    spades:
      rules:
        - rule_type: arguments
          nice_value: 0
          fail_message: Something went wrong
          arguments:
            - careful: true
    default_destination: waffles_default
"""

iv13dict = {
    "spades": {},
    'default_destination': "waffles_default"
}
