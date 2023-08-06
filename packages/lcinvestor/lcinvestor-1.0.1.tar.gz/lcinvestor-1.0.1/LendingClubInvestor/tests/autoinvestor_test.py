#!/usr/bin/env python

import sys
import os
import unittest
import subprocess
import urllib
import traceback
from time import sleep

sys.path.insert(0, '.')
sys.path.insert(0, '../')
sys.path.insert(0, '../../')
import LendingClubInvestor
from LendingClubInvestor import AutoInvestor


class TestInvestorUtils(unittest.TestCase):
    """ Tests the utility functions, like prompt and isfloat """

    count = 0
    investor = False

    def setUp(self):
        self.count = 0
        self.investor = AutoInvestor()

    def assertStrictEqual(self, first, second, msg=None):
        isSame = first == second and type(first) == type(second)
        self.assertTrue(isSame, msg)

    def test_prompt(self):
        # User enters 'test'
        self.investor.get_input = lambda msg: 'test'
        self.assertEqual(self.investor.prompt('msg'), 'test')
        self.assertEqual(self.investor.prompt('msg', 'not test'), 'test')

    def test_prompt_prefill(self):
        # User enters empty string, select prefill
        self.investor.get_input = lambda msg: ''
        self.assertEqual(self.investor.prompt('msg'), '')
        self.assertEqual(self.investor.prompt('msg', 'not test'), 'not test')

    def test_prompt_yn(self):
        # Yes
        self.investor.get_input = lambda msg: 'y'
        self.assertTrue(self.investor.prompt_yn('msg'))
        self.investor.get_input = lambda msg: 'Y'
        self.assertTrue(self.investor.prompt_yn('msg'))
        self.investor.get_input = lambda msg: 'Yes'
        self.assertTrue(self.investor.prompt_yn('msg'))

        # No
        self.investor.get_input = lambda msg: 'n'
        self.assertFalse(self.investor.prompt_yn('msg'))
        self.investor.get_input = lambda msg: 'N'
        self.assertFalse(self.investor.prompt_yn('msg'))
        self.investor.get_input = lambda msg: 'No'
        self.assertFalse(self.investor.prompt_yn('msg'))

        # Invalid user input
        def get_input(msg):
            self.count += 1
            return 'Hi' if self.count == 1 else 'Y'
        self.investor.get_input = get_input
        self.assertTrue(self.investor.prompt_yn('msg'))
        self.assertEqual(self.count, 2)

    def test_prompt_yn_prefill(self):
        # User enters empty string, select prefill
        self.investor.get_input = lambda msg: ''
        self.assertTrue(self.investor.prompt_yn('msg', 'y'))
        self.assertFalse(self.investor.prompt_yn('msg', 'n'))

    def test_prompt_float(self):
        self.count = 0

        # Return empty string first, then string, finally a float value the last time asked
        def get_input(msg):
            self.count += 1
            if self.count == 1:
                return ''
            elif self.count == 2:
                return 'Hi'
            else:
                return '10.0'

        self.investor.get_input = get_input
        self.assertEqual(self.investor.prompt_float('msg'), 10.0)
        self.assertEqual(self.count, 3)

        # Values with commas
        self.investor.get_input = lambda msg: '1,000.1'
        self.assertEqual(self.investor.prompt_float('msg'), 1000.1)

    def test_prompt_float_prefill(self):
        # User enters empty string, select prefill
        self.investor.get_input = lambda msg: ''
        self.assertEqual(self.investor.prompt_float('msg', 10.1), 10.1)

    def test_prompt_int(self):

        # Return empty string first, then string, finally an int value the last time asked
        def get_input(msg):
            self.count += 1
            if self.count == 1:
                return ''
            elif self.count == 2:
                return 'Hi'
            else:
                return '10'

        self.investor.get_input = get_input
        self.assertEqual(self.investor.prompt_float('msg'), 10)
        self.assertEqual(self.count, 3)

        # Values with commas
        self.investor.get_input = lambda msg: '1,000.1'
        self.assertEqual(self.investor.prompt_float('msg'), 1000.1)

    def test_prompt_int_prefill(self):
        # User enters empty string, select prefill
        self.investor.get_input = lambda msg: ''
        self.assertEqual(self.investor.prompt_int('msg', 15), 15)

    def test_is_float(self):
        self.assertTrue(self.investor.isfloat('10'))
        self.assertTrue(self.investor.isfloat('11.5'))
        self.assertTrue(self.investor.isfloat('-13'))
        self.assertTrue(self.investor.isfloat(14.5))

        self.assertFalse(self.investor.isfloat('NotANumber'))
        self.assertFalse(self.investor.isfloat('PartNumber123'))

    def test_currency_to_number(self):
        self.assertStrictEqual(self.investor.currency_to_float('123.45'), 123.45)
        self.assertStrictEqual(self.investor.currency_to_float('$123.45'), 123.45)
        self.assertStrictEqual(self.investor.currency_to_float('123.45$'), 123.45)
        self.assertStrictEqual(self.investor.currency_to_float('123.45$USD'), 123.45)
        self.assertStrictEqual(self.investor.currency_to_float('1,230.45'), 1230.45)
        self.assertStrictEqual(self.investor.currency_to_float('123'), 123.0)
        self.assertStrictEqual(self.investor.currency_to_float('$123'), 123.0)


class TestInvestorFlow(unittest.TestCase):
    """ Tests the investor flow and communication with LendingClub """

    server = None
    investor = None

    def startNode(self):
        """ Start the node server, if it's not already running """

        # Check if it's running
        try:
            if urllib.urlopen('http://localhost:7357').getcode() == 200:
                return True
        except Exception:
            pass

        # Start
        baseDir = os.path.dirname(os.path.realpath(__file__))
        nodeServer = os.path.join(baseDir, 'node/server.js')
        self.server = subprocess.Popen('node {0}'.format(nodeServer), shell=True, stdout=subprocess.PIPE)
        sleep(.2)  # startup time

        return True

    def setUp(self):
        # Start dummy server
        self.startNode()

        # Create investor object
        self.investor = AutoInvestor()
        self.investor.baseUrl = 'http://localhost:7357'
        self.investor.settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.investortest')
        self.investor.settings = {
            'email': 'test@test.com',
            'pass': 'testpassword',
            'minCash': 100,
            'minPercent': 16.5,
            'maxPercent': 19.0,
            'portfolio': 'Existing Portfolio',
            'filters': False
        }
        self.investor.logger = TestLogger()

    def tearDown(self):
        # Stop node
        if(self.server):
            self.server.kill()

        # Delete settings file
        if os.path.exists(self.investor.settings_file):
            os.remove(self.investor.settings_file)

    def set_default_filters(self):
        """ Sets all the filters to default valeus (True) """
        self.investor.settings['filters'] = {
            'exclude_existing': True,
            'term36month': True,
            'term60month': True,
            'grades': {
                'All': True,
                'A': True,
                'B': True,
                'C': True,
                'D': True,
                'E': True,
                'F': True,
                'G': True
            }
        }

    def set_filters(self):
        """ Add advanced filtering to the investor settings """
        self.set_default_filters()
        self.investor.settings['filters']['term36month'] = False
        self.investor.settings['filters']['grades']['All'] = False
        self.investor.settings['filters']['grades']['D'] = False
        self.investor.settings['filters']['grades']['E'] = False
        self.investor.settings['filters']['grades']['F'] = False
        self.investor.settings['filters']['grades']['G'] = False

    def test_login(self):
        self.assertTrue(self.investor.authenticate())

    def test_invalid_login(self):
        self.investor.settings['email'] = 'wrong@wrong.com'
        self.assertFalse(self.investor.authenticate())

    def test_get_cash_balance(self):
        self.assertEqual(self.investor.get_cash_balance(), 216.02)

    def test_portfolios(self):
        portfolios = self.investor.get_portfolio_list()
        self.assertEquals(len(portfolios), 2)
        self.assertEquals(portfolios[0], 'Existing Portfolio')

    def test_investment_option(self):
        """ Match settings to investment options -- closest match should be 18.66 """
        match = self.investor.get_investment_option(200)
        self.assertEqual(match['percentage'], 18.66)

    def test_investment_option_minimums(self):
        """ Test min percent: no investment options between 18.7 - 19.0 """
        self.investor.settings['minPercent'] = 18.7
        match = self.investor.get_investment_option(200)
        self.assertFalse(match)

    def test_investment_options_summary(self):
        """ Test the options summary output """
        match = self.investor.get_investment_option(200)
        summary = self.investor.get_option_summary(match)
        expected = 'Investment portfolio summary: 8 loan notes. 13% in B, 38% in C, 13% in D, 13% in E, 25% in F.'
        self.assertEqual(summary, expected)

    def test_investment_option_filters_below_percent(self):
        """ Investment Options within below percent settings.
        With filters set, the fixture data will return options below the min/max percent settings """

        self.set_filters()
        match = self.investor.get_investment_option(200)
        self.assertFalse(match)

    def test_investment_option_filters_break_server_grades(self):
        """ test_investment_option_filters_break_server_grades
        Test the server logic for checking grades.
        The server is expecting A,B,C and should raise an error if it sees anything else"""

        self.set_filters()
        self.investor.settings['filters']['grades']['All'] = True
        self.investor.settings['filters']['grades']['G'] = True
        match = self.investor.get_investment_option(200)

        # Check for error
        self.assertFalse(match)
        self.assertEqual(len(self.investor.logger.errors), 1)

    def test_investment_option_filters_break_server_json(self):
        """ test_investment_option_filters_break_server_json
        Test the server logic for parsing the JSON feed.
        The server should raise an error for invalid JSON"""

        # Create a request with bad JSON
        formerFilterFunc = LendingClubInvestor.get_filter_json
        LendingClubInvestor.get_filter_json = lambda settings: '{invalid json feed,,}'
        match = self.investor.get_investment_option(200)

        # Check for error
        self.assertFalse(match)
        self.assertEqual(len(self.investor.logger.errors), 1)

        # Reset
        LendingClubInvestor.get_filter_json = formerFilterFunc

    def test_investment_option_filters_within_percent(self):
        """ Investment Options within percent settings.
        Set min/max settings to be within options returned with filters """

        self.set_filters()

        # Default min/max are 16.5 - 19.0, filtered results fixture only goes up to 15.03
        self.investor.settings['minPercent'] = 13.0
        self.investor.settings['maxPercent'] = 14.5
        match = self.investor.get_investment_option(200)
        self.assertEqual(match['percentage'], 14.5)  # should be a perfect match

    def test_investment_option_validate(self):
        """ test_investment_option_validate
        Test validating an option against advanced filters """
        match = self.investor.get_investment_option(200)

        # Initial match should be True
        self.assertEqual(match['percentage'], 18.66)
        self.assertTrue(self.investor.validate_option(match))

        # Set C to False, everything else true
        self.set_default_filters()
        self.assertTrue(self.investor.validate_option(match))  # defaults should be True
        self.investor.settings['filters']['grades']['All'] = False
        self.investor.settings['filters']['grades']['C'] = False
        self.assertFalse(self.investor.validate_option(match))  # False

        # Set 36 month to False, everything else true
        self.set_default_filters()
        self.assertTrue(self.investor.validate_option(match))  # defaults should be True
        self.investor.settings['filters']['term36month'] = False
        self.assertFalse(self.investor.validate_option(match))  # False

        # Set 60 month to False, everything else true
        self.set_default_filters()
        self.assertTrue(self.investor.validate_option(match))  # defaults should be True
        self.investor.settings['filters']['term60month'] = False
        self.assertFalse(self.investor.validate_option(match))  # False

    def test_prepare_order(self):
        investmentOption = self.investor.get_investment_option(200)
        strutToken = self.investor.prepare_investment_order(200, investmentOption)
        self.assertEqual(strutToken, 'abc123')

    def test_place_order(self):
        investmentOption = self.investor.get_investment_option(200)
        (orderID, loanIDs) = self.investor.place_order('abc123', 200, investmentOption)
        self.assertEqual(orderID, 123)
        self.assertEqual(loanIDs, [345])

    def test_assign_to_porfolio_existing(self):
        """ Assign to an existing portfolio """

        ret = self.investor.assign_to_portfolio(orderID=123, loanIDs=[456], returnJson=True)
        self.assertEqual(ret['result'], 'success')
        self.assertEqual(ret['portfolioName'], 'Existing Portfolio')  # hard coded in the JSON response

        # Should have no errors or warnings
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 0)

    def test_assign_to_porfolio_new(self):
        """ Assign to a new portfolio """

        self.investor.settings['portfolio'] = 'New Porfolio'
        ret = self.investor.assign_to_portfolio(orderID=123, loanIDs=[456], returnJson=True)
        self.assertEqual(ret['result'], 'success')
        self.assertEqual(ret['portfolioName'], 'New Portfolio')  # hard coded in the JSON response

        # Should have no errors or warnings
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 0)

    def test_assign_to_porfolio_incorrect_assignment(self):
        """ Test warning if order is assigned to the wrong portfolio.
        The server responds with JSON containing the portfolio name your order was assigned to.
        There's no reason to think these would be difference, but if they are, assign_to_portfolio
        should still return True, but add a warning to the log. (easy to test, since the mock
        server returns hard coded JSON) """

        self.investor.settings['portfolio'] = 'A Folio'  # server will respond with 'New Portfolio'
        ret = self.investor.assign_to_portfolio(orderID=123, loanIDs=[456])
        self.assertTrue(ret)

        # Should have 1 warnings and 0 errors
        self.assertEqual(len(self.investor.logger.warnings), 1)
        self.assertEqual(len(self.investor.logger.errors), 0)

    def test_assign_to_porfolio_no_order(self):
        """ Assigning to portfolio without an order ID """
        ret = self.investor.assign_to_portfolio(loanIDs=[456])
        self.assertFalse(ret)

    def test_assign_to_porfolio_no_loan(self):
        """ Assigning to portfolio without a loan ID """
        ret = self.investor.assign_to_portfolio(orderID=123)
        self.assertFalse(ret)

    def test_assign_to_porfolio_no_portfolio(self):
        """ Test if not assigning to porfolio assign_to_portfolio() should return True """
        self.investor.settings['portfolio'] = False
        ret = self.investor.assign_to_portfolio(orderID=123, loanIDs=[456])
        self.assertTrue(ret)

        # Should be no errors or info
        self.assertEqual(len(self.investor.logger.infos), 0)
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 0)

    def test_attempt_to_invest(self):
        """ test_attempt_to_invest() - Test end-to-end investment """
        ret = self.investor.attempt_to_invest()
        self.assertTrue(ret)

        # Shouldn't be any errors or warnings
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 0)

    def test_attempt_to_invest_no_folio(self):
        """ Test end-to-end investment without portfolio """
        self.investor.settings['portfolio'] = False
        ret = self.investor.attempt_to_invest()
        self.assertTrue(ret)

        # Shouldn't be any errors or warnings
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 0)

    def test_attempt_to_invest_not_enough_cash(self):
        """ Test end-to-end investment without portfolio """
        self.investor.settings['minCash'] = 1000
        ret = self.investor.attempt_to_invest()
        self.assertFalse(ret)

        # Shouldn't be any errors or warnings
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 0)

    def test_attempt_to_invest_no_option_match(self):
        """ Test end-to-end investment without investment option match """
        # No options between 18.7 - 19.0
        self.investor.settings['minPercent'] = 18.7
        ret = self.investor.attempt_to_invest()
        self.assertFalse(ret)

        # Should be 0 errors and 1 warning
        self.assertEqual(len(self.investor.logger.errors), 0)
        self.assertEqual(len(self.investor.logger.warnings), 1)


class TestLogger():
    """ A simple and incomplete replacement for logger for testing. All logs are added to arrays """

    infos = []
    errors = []
    warnings = []
    debugs = []

    def __init__(self):
        self.infos = []
        self.errors = []
        self.warnings = []
        self.debugs = []

    def info(self, msg):
        #print '\nINVESTOR INFO: {0}\n'.format(msg)
        self.infos.append(msg)

    def error(self, msg):
        self.errors.append(msg)
        print '\nINVESTOR ERROR: {0}'.format(msg)

        # Traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)

    def warning(self, msg):
        print '\nINVESTOR WARNING: {0}\n'.format(msg)
        self.warnings.append(msg)

    def debug(self, msg):
        #print 'INVESTOR DEBUG: {0}'.format(msg)
        self.debugs.append(msg)


if __name__ == '__main__':
    unittest.main()
