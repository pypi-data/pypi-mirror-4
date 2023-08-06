#!/usr/bin/env python
#
# Sends a browse notes request and responds with the JSON
#

import sys
import os
import json

sys.path.insert(0, '.')
sys.path.insert(0, '../')
sys.path.insert(0, '../../')
import LendingClubInvestor

baseDir = os.path.dirname(os.path.realpath(__file__))

investor = LendingClubInvestor.AutoInvestor()
investor.settings_file = os.path.join(baseDir, '.browsetest')

if False:
    investor.settings = {
        'email': 'test@test.com',
        'pass': 'testpassword',
        'minCash': 100,
        'minPercent': 16.5,
        'maxPercent': 19.0,
        'portfolio': 'Existing Portfolio',
        'filters': {
            'exclude_existing': True,
            'term36month': True,
            'term60month': True,
            'grades': {
                'All': False,
                'A': True,
                'B': True,
                'C': True,
                'D': False,
                'E': False,
                'F': False,
                'G': False
            }
        }
    }
    print investor.prepare_filter_json()
else:
    investor.setup()
    results = investor.browse_notes()
    print '\nJSON RESULT'
    print json.dumps(results)
