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
        condition1:
            type: "filesize"
            nice: 0
            lbound: "0"
            hbound: "100000000"
            action: "things"
    default:
        destinationID: "default"
        runner: "a runner"
"""

vdictTest1_yml = {
    "spades": {
        "condition1": {
            "type": "filesize",
            'nice': 0,
            "lbound": "0",
            "hbound": "100000000",
            "action": "things"
        }
    },
    'default': {
        'runner': 'a runner',
         'destinationID': 'default'
    }
}

# Multiple jobs, multiple conditions
vYMLTest2 ='''
    spades:
        condition1:
            type: "default"
            action: "stuff"
    smalt:
        condition1:
            type: "filesize"
            nice: 0
            lbound: "0"
            hbound: "100000000"
            err_msg: "Too few reads for smalt to work"
            action: "fail"
        condition2:
            type: "filesize"
            nice: 0
            lbound: "100000000"
            hbound: "infinity"
            err_msg: "Too few reads for smalt to work"
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

vdictTest2_yml = {
    "spades": {
        "condition1": {
            "type": "default",
            "action": "stuff"
        }
    },
    "smalt": {
        "condition1": {
            "type": "filesize",
            'nice': 0,
            "lbound": "0",
            "hbound": "100000000",
            "err_msg": "Too few reads for smalt to work",
            "action": "fail"
        },
        "condition2": {
            "type": "filesize",
            'nice': 0,
            "lbound": "100000000",
            "hbound": "infinity",
            "err_msg": "Too few reads for smalt to work",
            "action": "fail"
        }
    },
    'default': {
        'runner': 'a runner',
         'destinationID': 'default'
    }
}

# Condition with extra attribute
vYMLTest3 = '''
    spades:
        condition1:
            type: "filesize"
            nice: 0
            hax: "002"
            lbound: 0
            hbound: 100000000
            err_msg: "Too few reads for spades to work"
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

vdictTest3_yml = {
    "spades": {
        "condition1": {
            "type": "filesize",
            'nice': 0,
            "hax": "002",
            "lbound": 0,
            "hbound": 100000000,
            "err_msg": "Too few reads for spades to work",
            "action": "fail"
        }
    },
    'default': {
        'runner': 'a runner',
         'destinationID': 'default'
    }
}

# Parameter type
vYMLTest4 = """
    spades:
        condition1:
            type: "parameter"
            nice: 0
            args:
                careful: true
            err_msg: "Failure"
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
"""

vdictTest4_yml = {
    "spades": {
        "condition1": {
            "type": "parameter",
            'nice': 0,
            "args": {
                "careful": True,
            },
            "err_msg": "Failure",
            "action": "fail"
        }
    },
    'default': {
        'runner': 'a runner',
         'destinationID': 'default'
    }
}

#=====================================================Invalid XML tests==========================================================

# Job with extra attribute
ivYMLTest1 = '''
    spades:
        age: 5
        condition1:
            type: "filesize"
            nice: 0
            lbound: 0
            hbound: 100000000
            err_msg: "Too few reads for spades to work"
            action: "fail" 
    default:
        destinationID: "default"
        runner: "a runner"
'''

# Empty file
ivYMLTest2 = ""

# Job without name
ivYMLTest3 = '''
    condition1:
        type: "filesize"
        nice: 0
        hbound: 100
        lbound: 0
        action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

iv3dict = {
    'default': {
        'runner': 'a runner',
        'destinationID': 'default'
    }, 
    'condition1': {}
}

# Condition missing type
ivYMLTest4 = '''
    spades:
        condition1:
            nice: 0
            lbound: "0"
            hbound: "0"
            err_msg: "No type..."
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

# Condition missing attribute
ivYMLTest51 = '''
    spades:
        condition1:
            type: "filesize"
            nice: 0
            hbound: "0"
            err_msg: "No type..."
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

# Condition missing attribute
ivYMLTest52 = '''
    spades:
        condition1:
            type: "filesize"
            nice: 0
            lbound: "0"
            err_msg: "No type..."
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

# Condition missing attribute
ivYMLTest53 = '''
    spades:
        condition1:
            type: "filesize"
            nice: 0
            lbound: "0"
            hbound: "0"
            err_msg: "No type..."
    default:
        destinationID: "default"
        runner: "a runner"
'''

# Condition unknown type
ivYMLTest6 = '''
    spades:
        condition1:
            type: "iencs"
            nice: 0
            lbound: "0"
            hbound: "0"
            err_msg: "No type..."
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

ivDict = {
    'default': {
        'runner': 'a runner', 
        'destinationID': 'default'
    }, 
    'spades': {}
}

# Default no destinationID
ivYMLTest7 = '''
    default:
        runner: "drmaa"
'''

# Default no runner
ivYMLTest8 = '''
    default:
        destinationID: "dest"
'''

# Tool condition fail no err_msg
ivYMLTest91 = '''
    spades:
        condition1:
            type: "filesize"
            lbound: "0"
            hbound: "0"
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

iv91dict = {
    'default': {
        'runner': 'a runner',
        'destinationID': 'default'
    },
    'spades': {
        'condition1': {
            'lbound': '0',
            'nice': 0,
            'type': 'filesize',
            'hbound': '0',
            'action': 'fail'
        }
    }
}

# Tool default fail no err_msg
ivYMLTest92 = '''
    spades:
        condition1:
            type: "default"
            lbound: "0"
            hbound: "0"
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
'''

iv92dict = {
    'default': {
        'runner': 'a runner',
        'destinationID': 'default'
    },
    'spades': {
        'condition1': {
            'lbound': '0',
            'type': 'default',
            'hbound': '0',
            'action': 'fail'
        }
    }
}

# Tool default fail no action
ivYMLTest10 = '''
    spades:
        condition1:
            type: "default"
            lbound: "0"
            hbound: "0"
    default:
        destinationID: "default"
        runner: "a runner"
'''

ivYMLTest11 = '''
    spades:
        condition1:
            type: "filesize"
            nice: "-21"
            lbound: "1 KB" 
            hbound: "infinity"
            action: "-q test.q -pe galaxy 4 -l h_vmem=2G"
        condition2:
            type: "default"
            action: "-q test.q -pe galaxy 16 -l h_vmem=2G"
    default:
        destinationID: "default"
        runner: "a runner"
'''

# Parameter fail no err_msg
ivYMLTest12 = """
    spades:
        condition1:
            type: "parameter"
            nice: 0
            args:
                careful: true
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
"""

iv12dict = {
    "spades": {
        "condition1": {
            "type": "parameter",
            'nice': 0,
            "args": {
                "careful": True,
            },
            "action": "fail"
        }
    },
    'default': {
        'runner': 'a runner',
         'destinationID': 'default'
    }
}

# Parameter fail no args
ivYMLTest131 = """
    spades:
        condition1:
            type: "parameter"
            nice: 0
            err_msg: "No args"
            action: "fail"
    default:
        destinationID: "default"
        runner: "a runner"
"""

# Parameter fail no action
ivYMLTest132 = """
    spades:
        condition1:
            type: "parameter"
            nice: 0
            args:
                careful: true
    default:
        destinationID: "default"
        runner: "a runner"
"""

iv13dict = {
    "spades": {},
    'default': {
        'runner': 'a runner',
         'destinationID': 'default'
    }
}
