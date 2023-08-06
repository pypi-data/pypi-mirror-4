#!/usr/bin/env python

"""
The MIT License (MIT)

Copyright (c) 2013 Jeremy Gillick

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys
import os
import re
import logging
import getpass
import requests
import json
import traceback
from time import sleep
from bs4 import BeautifulSoup
from util import *


class AutoInvestor:

    baseUrl = 'https://www.lendingclub.com/'
    authed = False
    cookies = {}
    isDaemon = False
    verbose = False
    loopDelay = 60 * 30  # 30 minutes in between loops

    homeDir = os.path.expanduser('~')
    baseDir = os.path.dirname(os.path.realpath(__file__))
    appDir = os.path.join(homeDir, '.lcinvestor')
    logFile = os.path.join(appDir, 'daemon.log')
    settings_file = os.path.join(appDir, 'settings.json')

    requestHeaders = {
        'Referer': 'https://www.lendingclub.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31'
    }

    # Defines the investment funding options
    settings = {
        'email': False,
        'pass': False,
        'minCash': 500,
        'minPercent': False,
        'maxPercent': False,
        'portfolio': False,
        'filters': False
    }

    def __init__(self, verbose=False, daemon=False):
        self.isDaemon = daemon
        self.verbose = verbose
        self.create_logger()

        # Setup user directory
        if os.path.exists(self.appDir) and not os.path.isdir(self.appDir):
            raise AutoInvestorError('The path \'{0}\' is not a directory.'.format(self.appDir))
        elif not os.path.exists(self.appDir):
            os.mkdir(self.appDir)

        # Daemon settings
        if daemon:
            self.stdin_path = '/dev/null'
            self.stdout_path = self.logFile
            self.stderr_path = self.logFile
            self.pidfile_path = '/tmp/investor.pid'
            self.pidfile_timeout = 1

    def setup(self):
        """
        Setup the investor to run
        """

        print "\n///--------------------------- $$$ ---------------------------\\\\\\"
        print '|    Welcome to the unofficial Lending Club investment tool     |'
        print " ---------------------------------------------------------------- \n"

        if self.verbose:
            print 'VERBOSE OUTPUT IS ON\n'

        # Load saved settings
        self.load_saved_settings()

        # Auth settings
        self.get_auth_settings()

        if self.authed:

            # Investment settings
            print 'Now that you\'re signed in, let\'s define what you want to do\n'

            # Use the settings from last time
            if self.settings['minPercent'] is not False and self.settings['maxPercent'] is not False:
                self.show_summary('Prior Settings')
                if not self.prompt_yn('Would you like to use these settings from last time?', 'y'):
                    self.get_investment_settings()
            else:
                self.get_investment_settings()

            # All ready to start running
            print '\nThat\'s all we need. Now, as long as this is running, your account will be checked every 30 minutes and invested if enough funds are available.\n'

    def run(self):
        """
        Start the auto investor loop which will check the LendingClub account every 30 minutes for
        funds to invest
        """
        self.investment_loop()

    def create_logger(self):
        """
        Initialize the logger
        """

        self.logger = logging.getLogger('investor')
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        logHandler = logging.StreamHandler()
        if self.verbose:
            logHandler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s #%(lineno)d - %(message)s', '%Y-%m-%d %H:%M'))
        else:
            logHandler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s - %(message)s', '%Y-%m-%d %H:%M'))

        self.logger.addHandler(logHandler)

    def currency_to_float(self, cashValue):
        """
        Converts a currency value, with or without symbols, to a floating point number,
        Returns -1.0, if the string is not a number or currency value
        """
        cash = -1.0
        try:
            # Match values like $1,000.12 or 1,0000$
            cashMatch = re.search('^[^0-9]?([0-9\.,]+)[^0-9]?', cashValue)
            if cashMatch:
                cashStr = cashMatch.group(1)
                cashStr = cashStr.replace(',', '')
                cash = float(cashStr)
        except Exception as e:
            self.logger.error('Could not convert the currency value \'{0}\' to a float number. Error: {1}'.format(cashValue, str(e)))

        return cash

    def isfloat(self, string):
        """
        Returns true if the string can be cast to a float
        """
        try:
            float(string)
            return True
        except ValueError:
            return False

    def save_settings(self):
        """
        Save the settings dict to a file
        """
        try:
            # Remove password
            settingsCopy = self.settings.copy()
            if 'pass' in settingsCopy:
                del(settingsCopy['pass'])

            # Convert to JSON
            jsonOut = json.dumps(settingsCopy)

            # Save
            self.logger.debug('Saving settings: {0}'.format(jsonOut))
            settingsFile = self.settings_file

            f = open(settingsFile, 'w')
            f.write(jsonOut)
            f.close()

            self.logger.debug('Saved')

        except Exception as e:
            self.logger.warning('Could not save the settings to file: {0}'.format(str(e)))

    def load_saved_settings(self):
        """
        Returned the saved settings used last time this program was run
        """
        settingsFile = self.settings_file
        if os.path.exists(settingsFile):
            self.logger.debug('Loading saved settings file')
            try:
                # Read file
                f = open(settingsFile, 'r')
                jsonStr = f.read()
                f.close()

                self.logger.debug('Saved settings: {0}'.format(jsonStr))

                # Convert JSON to dictionary
                savedSettings = json.loads(jsonStr)

                # Add values to dictionary
                for key, value in self.settings.iteritems():
                    if key in savedSettings:
                        self.settings[key] = savedSettings[key]

                # Migrations
                if '36month' in self.settings['filters']:
                    self.settings['filters']['term36month'] = self.settings['filters']['36month']
                    del self.settings['filters']['36month']

                if '60month' in self.settings['filters']:
                    self.settings['filters']['term60month'] = self.settings['filters']['60month']
                    del self.settings['filters']['60month']

            except Exception as e:
                self.logger.debug('Could not read settings file: {0}'.format(str(e)))
        else:
            self.logger.debug('No saved settings file to load')

    def post_url(self, relUrl, params={}, data={}, useCookies=True):
        """
        Sends POST request to the relative URL of www.lendingclub.com
        """
        url = '{0}{1}'.format(self.baseUrl, relUrl)
        self.logger.debug('POSTING {0}'.format(url))
        cookies = self.cookies if useCookies else {}
        return requests.post(url, params=params, data=data, cookies=cookies, headers=self.requestHeaders)

    def get_url(self, relUrl, params={}, useCookies=True):
        """
        Sends GET request to the relative URL of www.lendingclub.com
        """
        url = '{0}{1}'.format(self.baseUrl, relUrl)
        self.logger.debug('GETTING {0}'.format(url))
        cookies = self.cookies if useCookies else {}
        return requests.get(url, params=params, cookies=cookies, headers=self.requestHeaders)

    def get_password(self):
        """
        Wrapper for getpass.getpas that can be overridden for unit testing
        """
        return getpass.getpass()

    def get_input(self, msg):
        """
        Wrapper for raw_input that can be overridden for unit testing
        """
        return raw_input(msg)

    def prompt(self, msg, prefill=False):
        """
        Prompt the user for input and return the prefill value if the user does not enter anything
        """
        if prefill is not False:
            msg = "{0} [{1}]: ".format(msg, str(prefill))
        else:
            msg = "{0}: ".format(msg)

        response = self.get_input(msg)
        if response.strip() == '' and prefill is not False:
            return prefill
        else:
            return response

    def prompt_float(self, msg, prefill=False):
        """ Prompts the user for an decimal response """
        while(True):
            response = self.prompt(msg, prefill)

            # Remove commas
            if type(response) == str:
                response = response.replace(',', '')

            if type(response) == float:
                return response
            if not self.isfloat(response):
                print 'The value you entered must be a whole number, without symbols or decimal points'
            else:
                return float(response)

    def prompt_int(self, msg, prefill=False):
        """ Prompts the user for an integer response """
        while(True):
            response = self.prompt(msg, prefill)

            # Remove commas
            if type(response) == str:
                response = response.replace(',', '')

            # Validate response
            if type(response) == int:
                return response
            if not response.isdigit():
                print 'The value you entered must be a whole number, without symbols or decimal points'
            else:
                return int(response)

    def prompt_yn(self, msg, default=None):
        """
        Prompts the user for a y/n response.
        default param should be either 'y' or 'n'
        Returns True if 'Y' and False if 'N'
        """
        if default is True:
            default = 'y'
        elif default is False:
            default = 'n'

        if default == 'y' or default is True:
            msg = "{0} [Y/n]: ".format(msg)
        elif default == 'n':
            msg = "{0} [y/N]: ".format(msg)
        else:
            msg = "{0} [y/n]: ".format(msg)

        while(True):
            response = self.get_input(msg)

            # Normalize response
            response = response.lower().strip()
            if response == '' and default is not False:
                response = default

            # Return if valid
            if response in ['y', 'yes'] or response is True:
                return True
            elif response in ['n', 'no']:
                return False

    def prepare_filter_json(self):
        """
        DEPRECATED. Use util.get_filter_json()
        Convert the filter dictionary into the JSON that LendingClub expects
        """

        # Start with JSON from LendingClub that has all options
        baseJson = json.loads('[{"m_id":39,"m_metadata":{"m_controlValues":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}],"m_type":"MVAL","m_rep":"CHKBOX","m_label":"Term (36 - 60 month)","id":39,"m_onHoverHelp":"Select the loan maturities you are interested to invest in","m_className":"classname","m_defaultValue":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}]},"m_value":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}],"m_visible":false,"m_position":0},{"m_id":38,"m_metadata":{"m_controlValues":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}],"m_type":"SVAL","m_rep":"CHKBOX","m_label":"Exclude Loans already invested in","id":38,"m_onHoverHelp":"Use this filter to exclude loans from a borrower that you have already invested in.","m_className":"classname","m_defaultValue":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}]},"m_value":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}],"m_visible":false,"m_position":0},{"m_id":10,"m_metadata":{"m_controlValues":[{"value":"All","label":"All","sqlValue":null,"valueIndex":0},{"value":"D","label":"<span class=\\"grades d-loan-grade\\">D</span> 18.76%","sqlValue":null,"valueIndex":1},{"value":"A","label":"<span class=\\"grades a-loan-grade\\">A</span> 7.41%","sqlValue":null,"valueIndex":2},{"value":"E","label":"<span class=\\"grades e-loan-grade\\">E</span> 21.49%","sqlValue":null,"valueIndex":3},{"value":"B","label":"<span class=\\"grades b-loan-grade\\">B</span> 12.12%","sqlValue":null,"valueIndex":4},{"value":"F","label":"<span class=\\"grades f-loan-grade\\">F</span> 23.49%","sqlValue":null,"valueIndex":5},{"value":"C","label":"<span class=\\"grades c-loan-grade\\">C</span> 15.80%","sqlValue":null,"valueIndex":6},{"value":"G","label":"<span class=\\"grades g-loan-grade\\">G</span> 24.84%","sqlValue":null,"valueIndex":7}],"m_type":"MVAL","m_rep":"CHKBOX","m_label":"Interest Rate","id":10,"m_onHoverHelp":"Specify the interest rate ranges of the notes  you are willing to invest in.","m_className":"short","m_defaultValue":[{"value":"All","label":"All","sqlValue":null,"valueIndex":0}]},"m_value":[{"value":"D","label":"<span class=\\"grades d-loan-grade\\">D</span> 18.76%","sqlValue":null,"valueIndex":1},{"value":"A","label":"<span class=\\"grades a-loan-grade\\">A</span> 7.41%","sqlValue":null,"valueIndex":2},{"value":"E","label":"<span class=\\"grades e-loan-grade\\">E</span> 21.49%","sqlValue":null,"valueIndex":3},{"value":"B","label":"<span class=\\"grades b-loan-grade\\">B</span> 12.12%","sqlValue":null,"valueIndex":4},{"value":"F","label":"<span class=\\"grades f-loan-grade\\">F</span> 23.49%","sqlValue":null,"valueIndex":5},{"value":"C","label":"<span class=\\"grades c-loan-grade\\">C</span> 15.80%","sqlValue":null,"valueIndex":6},{"value":"G","label":"<span class=\\"grades g-loan-grade\\">G</span> 24.84%","sqlValue":null,"valueIndex":7}],"m_visible":false,"m_position":0},{"m_id":37,"m_metadata":{"m_controlValues":null,"m_type":"SVAL","m_rep":"TEXTBOX","m_label":"Keyword","id":37,"m_onHoverHelp":"Type any keyword","m_className":"classname","m_defaultValue":[]},"m_value":null,"m_visible":false,"m_position":0}]')
        sendJson = list(baseJson)

        # No filters set
        if not self.settings['filters']:
            return False

        # Walk through the JSON that has ALL settings and remove the ones we've marked as False
        for i, field in enumerate(sendJson):
            fieldId = field['m_id']

            # Replace m_value with m_controlValues
            if type(field['m_metadata']['m_controlValues']) is list:
                field['m_value'] = list(field['m_metadata']['m_controlValues'])

            fieldValues = field['m_value']

            # Term (36 - 60 month)
            if fieldId == 39:

                v = 0
                while(v < len(fieldValues)):
                    value = fieldValues[v]
                    if value['value'] == 'Year3' and not self.settings['filters']['term36month']:
                        del fieldValues[v]
                    elif value['value'] == 'Year5' and not self.settings['filters']['term60month']:
                        del fieldValues[v]

                    # Only increment if nothing was removed (removing changes the index)
                    else:
                        v += 1

            # Exclude Loans already invested in
            elif fieldId == 38:
                if not self.settings['filters']['exclude_existing']:
                    del fieldValues[0]

            # Interest rate grades
            elif fieldId == 10:

                v = 0
                while(v < len(fieldValues)):
                    value = fieldValues[v]
                    valName = value['value']

                    # Match the All, A - G to the Grade filters, if False, remove
                    # if All is True, remove everything but the All field
                    if self.settings['filters']['grades'][valName] is False or (self.settings['filters']['grades']['All'] is True and valName != 'All'):
                        del fieldValues[v]
                        v -= 1

                    # Increment
                    v += 1

        sendJson = json.dumps(sendJson)
        #sendJson = sendJson.replace('"', '\\"')
        print sendJson
        #return '[{"m_id":39,"m_metadata":{"m_controlValues":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}],"m_type":"MVAL","m_rep":"CHKBOX","m_label":"Term (36 - 60 month)","id":39,"m_onHoverHelp":"Select the loan maturities you are interested to invest in","m_className":"classname","m_defaultValue":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}]},"m_value":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}],"m_visible":false,"m_position":0},{"m_id":38,"m_metadata":{"m_controlValues":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}],"m_type":"SVAL","m_rep":"CHKBOX","m_label":"Exclude Loans already invested in","id":38,"m_onHoverHelp":"Use this filter to exclude loans from a borrower that you have already invested in.","m_className":"classname","m_defaultValue":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}]},"m_value":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}],"m_visible":false,"m_position":0},{"m_id":10,"m_metadata":{"m_controlValues":[{"value":"All","label":"All","sqlValue":null,"valueIndex":0},{"value":"D","label":"<span class=\\"grades d-loan-grade\\">D</span> 18.76%","sqlValue":null,"valueIndex":1},{"value":"A","label":"<span class=\\"grades a-loan-grade\\">A</span> 7.41%","sqlValue":null,"valueIndex":2},{"value":"E","label":"<span class=\\"grades e-loan-grade\\">E</span> 21.49%","sqlValue":null,"valueIndex":3},{"value":"B","label":"<span class=\\"grades b-loan-grade\\">B</span> 12.12%","sqlValue":null,"valueIndex":4},{"value":"F","label":"<span class=\\"grades f-loan-grade\\">F</span> 23.49%","sqlValue":null,"valueIndex":5},{"value":"C","label":"<span class=\\"grades c-loan-grade\\">C</span> 15.80%","sqlValue":null,"valueIndex":6},{"value":"G","label":"<span class=\\"grades g-loan-grade\\">G</span> 24.84%","sqlValue":null,"valueIndex":7}],"m_type":"MVAL","m_rep":"CHKBOX","m_label":"Interest Rate","id":10,"m_onHoverHelp":"Specify the interest rate ranges of the notes  you are willing to invest in.","m_className":"short","m_defaultValue":[{"value":"All","label":"All","sqlValue":null,"valueIndex":0}]},"m_value":[{"value":"A","label":"<span class=\\"grades a-loan-grade\\">A</span> 7.41%","sqlValue":null,"valueIndex":2},{"value":"B","label":"<span class=\\"grades b-loan-grade\\">B</span> 12.12%","sqlValue":null,"valueIndex":4},{"value":"C","label":"<span class=\\"grades c-loan-grade\\">C</span> 15.80%","sqlValue":null,"valueIndex":6}],"m_visible":false,"m_position":0},{"m_id":37,"m_metadata":{"m_controlValues":null,"m_type":"SVAL","m_rep":"TEXTBOX","m_label":"Keyword","id":37,"m_onHoverHelp":"Type any keyword","m_className":"classname","m_defaultValue":[]},"m_value":null,"m_visible":false,"m_position":0}]'
        return sendJson

    def browse_notes(self):
        """
        Sends the filters to the Browse Notes API and returns a JSON of the notes found
        """
        try:

            # Get all investment options
            filters = get_filter_json(self.settings['filters'])
            print 'Filter!\n', filters
            if filters is False:
                filters = 'default'
            payload = {
                'method': 'search',
                'filter': filters
                #'filter': '[{"m_id":39,"m_metadata":{"m_controlValues":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}],"m_type":"MVAL","m_rep":"CHKBOX","m_label":"Term (36 - 60 month)","id":39,"m_onHoverHelp":"Select the loan maturities you are interested to invest in","m_className":"classname","m_defaultValue":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}]},"m_value":[{"value":"Year3","label":"36-month","sqlValue":null,"valueIndex":0},{"value":"Year5","label":"60-month","sqlValue":null,"valueIndex":1}],"m_visible":false,"m_position":0},{"m_id":38,"m_metadata":{"m_controlValues":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}],"m_type":"SVAL","m_rep":"CHKBOX","m_label":"Exclude Loans already invested in","id":38,"m_onHoverHelp":"Use this filter to exclude loans from a borrower that you have already invested in.","m_className":"classname","m_defaultValue":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}]},"m_value":[{"value":true,"label":"Exclude loans invested in","sqlValue":null,"valueIndex":0}],"m_visible":false,"m_position":0},{"m_id":10,"m_metadata":{"m_controlValues":[{"value":"All","label":"All","sqlValue":null,"valueIndex":0},{"value":"D","label":"<span class=\\"grades d-loan-grade\\">D</span> 18.76%","sqlValue":null,"valueIndex":1},{"value":"A","label":"<span class=\\"grades a-loan-grade\\">A</span> 7.41%","sqlValue":null,"valueIndex":2},{"value":"E","label":"<span class=\\"grades e-loan-grade\\">E</span> 21.49%","sqlValue":null,"valueIndex":3},{"value":"B","label":"<span class=\\"grades b-loan-grade\\">B</span> 12.12%","sqlValue":null,"valueIndex":4},{"value":"F","label":"<span class=\\"grades f-loan-grade\\">F</span> 23.49%","sqlValue":null,"valueIndex":5},{"value":"C","label":"<span class=\\"grades c-loan-grade\\">C</span> 15.80%","sqlValue":null,"valueIndex":6},{"value":"G","label":"<span class=\\"grades g-loan-grade\\">G</span> 24.84%","sqlValue":null,"valueIndex":7}],"m_type":"MVAL","m_rep":"CHKBOX","m_label":"Interest Rate","id":10,"m_onHoverHelp":"Specify the interest rate ranges of the notes  you are willing to invest in.","m_className":"short","m_defaultValue":[{"value":"All","label":"All","sqlValue":null,"valueIndex":0}]},"m_value":[{"value":"A","label":"<span class=\\"grades a-loan-grade\\">A</span> 7.41%","sqlValue":null,"valueIndex":2},{"value":"B","label":"<span class=\\"grades b-loan-grade\\">B</span> 12.12%","sqlValue":null,"valueIndex":4},{"value":"C","label":"<span class=\\"grades c-loan-grade\\">C</span> 15.80%","sqlValue":null,"valueIndex":6}],"m_visible":false,"m_position":0},{"m_id":37,"m_metadata":{"m_controlValues":null,"m_type":"SVAL","m_rep":"TEXTBOX","m_label":"Keyword","id":37,"m_onHoverHelp":"Type any keyword","m_className":"classname","m_defaultValue":[]},"m_value":null,"m_visible":false,"m_position":0}]'
            }
            response = self.post_url('/browse/browseNotesAj.action', data=payload)
            jsonRes = response.json()
            return jsonRes

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)
            self.logger.error(str(e))
            return False

    def validate_option(self, option):
        """
        Validate a chosen investment option by the advanced filters
        """
        ok = True
        filters = self.settings['filters']

        # No advanced filters
        if filters is False:
            return True

        # Check grades
        if filters['grades']['All'] is not True:
            for grade in filters['grades']:
                value = filters['grades'][grade]
                grade = grade.lower()

                # Has notes in a grade that should be excluded
                if value is False and grade in option and option[grade] > 0:
                    ok = False
                    break

        # Check terms
        if filters['term36month'] is False and 'percent_of_year3_loans' in option and option['percent_of_year3_loans'] > 0:
            ok = False
        if filters['term60month'] is False and 'percent_of_year5_loans' in option and option['percent_of_year5_loans'] > 0:
            ok = False

        # Did not pass!
        if not ok:
            self.logger.error('The investment options found did not match your term or grade requirements. It seems like the advanced filtering code might be broken! Either fix the code or stop using the advanced filters.')

        return ok

    def get_investment_option(self, cash):
        """
        When investing, lending club provides a list of investment portfolio options, all with different
        diversification of loan classes which come out to an average percent return.

        This method returns an investment option that best matches your available cash and min/max
        percentage (defined in settings) desired. If there are multiple options between min & max,
        the one closest to max will be chosen.
        """
        try:
            maxPercent = self.settings['maxPercent']
            minPercent = self.settings['minPercent']

            # Get all investment options
            filters = get_filter_json(self.settings['filters'])
            if filters is False:
                filters = 'default'
            payload = {
                'amount': cash,
                'max_per_note': 0,
                'filter': filters
            }
            response = self.post_url('/portfolio/lendingMatchOptionsV2.action', data=payload)
            json = response.json()

            if json['result'] == 'success' and 'lmOptions' in json:
                options = json['lmOptions']
                lastOption = False

                # Loop through all the investment options
                i = 0
                for option in options:
                    option['optIndex'] = i

                    # A perfect match
                    if option['percentage'] == maxPercent:
                        return option

                    # Over the max
                    elif option['percentage'] > maxPercent:
                        break

                    # Over the minimum
                    elif option['percentage'] >= minPercent:
                        lastOption = option

                    i += 1

                # If the perfect match wasn't found, return the last
                # option that was under the maximum percent
                return lastOption
            else:
                self.logger.error('Could not get investment portfolio options! Server responded with: {0}'.format(response.text))
                return False

        except Exception as e:
            self.logger.error(str(e))

        return False

    def get_option_summary(self, investmentOption):
        """
        Log a summary of the investment option which was ordered
        """
        summary = 'Investment portfolio summary: {0} loan notes. '.format(investmentOption['numberOfLoans'])

        breakdown = []
        for grade in ['a', 'aa', 'b', 'c', 'd', 'e', 'f', 'g']:
            if investmentOption[grade] > 0.0:
                percent = int(round(investmentOption[grade]))
                grade = grade.upper()
                breakdown.append('{0}% in {1}'.format(percent, grade))

        if len(breakdown) > 0:
            summary += ', '.join(breakdown)
            summary += '.'

        return summary

    def get_strut_token(self):
        """
        Get the struts token from the place order page
        """
        strutToken = ''
        try:
            response = self.get_url('/portfolio/placeOrder.action')
            soup = BeautifulSoup(response.text, "html5lib")
            strutTokenTag = soup.find('input', {'name': 'struts.token'})
            if strutTokenTag:
                strutToken = strutTokenTag['value']
        except Exception as e:
            self.logger.warning('Could not get struts token. Error message: {0}'.filter(str(e)))

        return strutToken

    def prepare_investment_order(self, cash, investmentOption):
        """
        Submit an investment request for with an investment portfolio option selected from get_investment_option()
        """

        # Place the order
        try:
            if 'optIndex' not in investmentOption:
                self.logger.error('The \'optIndex\' key is not present in investmentOption passed to sendInvestment()! This value is set when selecting the option from get_investment_option()')
                return False

            # Prepare the order (don't process response)
            payload = {
                'order_amount': cash,
                'lending_match_point': investmentOption['optIndex'],
                'lending_match_version': 'v2'
            }
            self.get_url('/portfolio/recommendPortfolio.action', params=payload)

            # Get struts token
            return self.get_strut_token()

        except Exception as e:
            self.logger.error('Could not complete your order (although, it might have gone through): {0}'.format(str(e)))

        return False

    def place_order(self, strutToken, cash, investmentOption):
        """
        Place the order and get the order number, loan ID from the resulting HTML -- then assign to a portfolio
        The cash parameter is the amount of money invest in this order
        The investmentOption parameter is the investment portfolio returned by get_investment_option()
        """

        orderID = 0
        loanIDs = []

        # Process order confirmation page
        try:
            payload = {}
            if strutToken:
                payload['struts.token.name'] = 'struts.token'
                payload['struts.token'] = strutToken
            response = self.post_url('/portfolio/orderConfirmed.action', data=payload)

            # Process HTML
            html = response.text
            soup = BeautifulSoup(html)

            # Order num
            orderField = soup.find(id='order_id')
            if orderField:
                orderID = int(orderField['value'])

            # Load ID
            loanTags = soup.find_all('td', {'class': 'loan_id'})
            for tag in loanTags:
                loanIDs.append(int(tag.text))

            # Print status message
            if orderID == 0:
                self.logger.error('An investment order was submitted, but a confirmation could not be determined')
            else:
                self.logger.info('Order #{0} was successfully submitted for ${1} at {2}%'.format(orderID, cash, investmentOption['percentage']))

            # Print order summary
            self.logger.info(self.get_option_summary(investmentOption))

        except Exception as e:
            self.logger.error('Could not get your order number or loan ID from the order confirmation. Err Message: {0}'.format(str(e)))

        return (orderID, loanIDs)

    def assign_to_portfolio(self, orderID=0, loanIDs=[], returnJson=False):
        """
        Assign an order to a the portfolio named in the settings dictionary.
        If returnJson is true, this method will return the JSON from the server instead of True/False (this is primarily for unit testing)
        """

        # Assign to portfolio
        resText = ''
        try:
            if not self.settings['portfolio']:
                return True

            if len(loanIDs) != 0 and orderID != 0:

                # Data
                orderIDs = [orderID]*len(loanIDs)  # 1 order ID per record
                postData = {
                    'loan_id': loanIDs,
                    'record_id': loanIDs,
                    'order_id': orderIDs
                }
                paramData = {
                    'method': 'addToLCPortfolio',
                    'lcportfolio_name': self.settings['portfolio']
                }

                # New portfolio
                folioList = self.get_portfolio_list()
                if self.settings['portfolio'] not in folioList:
                    paramData['method'] = 'createLCPortfolio'

                # Send
                response = self.post_url('/data/portfolioManagement', params=paramData, data=postData)
                resText = response.text
                resJson = response.json()

                if returnJson is True:
                    return resJson

                # Failed if the response is not 200 or JSON result is not success
                if response.status_code != 200 or resJson['result'] != 'success':
                    self.logger.error('Could not assign order #{0} to portfolio \'{1}: Server responded with {2}\''.format(str(orderID), self.settings['portfolio'], response.text))

                # Success
                else:

                    # Assigned to another portfolio, for some reason, raise warning
                    if 'portfolioName' in resJson and resJson['portfolioName'] != self.settings['portfolio']:
                        self.logger.warning('Added order #{0} to portfolio "{1}" - NOT - "{2}", and I don\'t know why'.format(str(orderID), resJson['portfolioName'], self.settings['portfolio']))

                    # Return
                    else:
                        self.logger.info('Added order #{0} to portfolio "{1}"'.format(str(orderID), self.settings['portfolio']))

                    return True

        except Exception as e:
            self.logger.error('Could not assign order #{0} to portfolio \'{1}\': {2} -- {3}'.format(orderID, self.settings['portfolio'], str(e), resText))

        return False

    def get_cash_balance(self):
        """
        Returns the cash balance available to invest
        """
        cash = -1
        try:
            response = self.get_url('/browse/cashBalanceAj.action')
            json = response.json()

            if json['result'] == 'success':
                self.logger.debug('Cash available: {0}'.format(json['cashBalance']))
                cash = self.currency_to_float(json['cashBalance'])
            else:
                self.logger.error('Could not get cash balance: {0}'.format(response.text))

        except Exception as e:
            self.logger.error('Could not get the cash balance on the account: {0}\nJSON: {1}'.format(str(e), response.text))

        return cash

    def attempt_to_invest(self):
        """
        Attempt an investment if there is enough available cash and matching investment option
        Returns true if money was invested
        """

        # Authenticate
        if self.authenticate():
            self.logger.info('Authenticated')
        else:
            self.logger.error('Could not authenticate')
            return False

        # Try to invest
        self.logger.info('Checking for funds to invest...')
        try:
            # Get current cash balance
            allCash = self.get_cash_balance()
            if allCash > 0:

                # Find closest cash amount divisible by $25
                cash = int(allCash)
                while cash % 25 != 0:
                    cash -= 1

                # Invest
                self.logger.debug('Cash to invest: ${0} (of ${1} total)'.format(cash, allCash))
                if cash >= self.settings['minCash']:
                    self.logger.info('Attempting to investing ${0}'.format(cash))
                    option = self.get_investment_option(cash)

                    # Submit investment
                    if option and self.validate_option(option):
                        self.logger.info('Auto investing your available cash (${0}) at {1}%...'.format(cash, option['percentage']))
                        sleep(5)  # last chance to cancel

                        # Prepare the investment and place the order
                        strutToken = self.prepare_investment_order(cash, option)
                        if strutToken:
                            (orderID, loanIDs) = self.place_order(strutToken, cash, option)
                            if orderID > 0 and len(loanIDs) > 0:
                                self.assign_to_portfolio(orderID, loanIDs)
                                self.logger.info('Done\n')
                                return True

                        # If we haven't returned by now, there must have been an error
                        self.logger.error('Errors occurred. Will try again in 30 minutes\n')
                        return False

                    else:
                        self.logger.warning('No investment options are available at this time for portfolios between {0}% - {1}% -- Trying again in 30 minutes'.format(self.settings['minPercent'], self.settings['maxPercent']))
                else:
                    self.logger.info('Only ${0} available'.format(allCash))
                    return False

        except Exception as e:
            self.logger.error(str(e))

        return False

    def investment_loop(self):
        """
        Invest cash every 30 minutes
        """
        while(True):
            self.attempt_to_invest()

            # Sleep for 30 minutes and then authenticate and move to the main loop
            sleep(self.loopDelay)

    def authenticate(self):
        """
        Attempt to authenticate the user with the email/pass in the settings dictionary.
        Returns True/False
        """

        payload = {
            'login_email': self.settings['email'],
            'login_password': self.settings['pass']
        }
        response = self.post_url('/account/login.action', data=payload, useCookies=False)

        if (response.status_code == 200 or response.status_code == 302) and 'LC_FIRSTNAME' in response.cookies:
            self.authed = True
            self.cookies = response.cookies
            return True

        self.logger.error('Authentication returned {0}. Cookies: {1}'.format(response.status_code, str(response.cookies.keys())))
        return False

    def get_portfolio_list(self):
        """
        Return the list of portfolio names from the server
        """
        foliosNames = []
        try:
            response = self.get_url('/data/portfolioManagement?method=getLCPortfolios')
            json = response.json()

            # Get portfolios and create a list of names
            if json['result'] == 'success':
                folios = json['results']
                for folio in folios:
                    foliosNames.append(folio['portfolioName'])

        except Exception as e:
            self.logger.warning('Could not get list of portfolios for this account. Error message: {0}'.format(str(e)))

        return foliosNames

    def portfolio_picker(self, previousFolio=False):
        """
        Load existing portfolios and let the user choose one or create a new one
        """

        print '\nPortfolios...'

        try:
            folios = self.get_portfolio_list()

            # Print out the portfolio list
            i = 1
            otherIndex = 0
            cancelIndex = 0
            previousIndex = 0
            for folio in folios:
                print '{0}: {1}'.format(i, folio)

                if previousFolio == folio:
                    previousFolio = False

                i += 1

            if previousFolio is not False:
                previousIndex = i
                print '{0}: {1}'.format(previousIndex, previousFolio)
                i += 1

            otherIndex = i
            print '{0}: Other'.format(otherIndex)
            i += 1

            cancelIndex = i
            print '{0}: Cancel'.format(cancelIndex)

            # Choose a portfolio
            while(True):
                choice = self.prompt('Choose one')

                if not choice.isdigit():
                    continue
                choice = int(choice)

                # No zero
                if choice == 0:
                    continue

                # Existing portfolio chosen
                if choice <= len(folios):
                    break

                # Previous
                elif choice == previousIndex:
                    return previousFolio

                # Other
                elif choice == otherIndex:
                    while(True):
                        other = self.prompt('Enter the name for your new portfolio')

                        # Empty string entered, show list again
                        if other.strip() == '':
                            break

                        # Invalid character
                        elif re.search('[^a-zA-Z0-9 ,_\-#\.]', other):
                            print 'The portfolio name is not valid, only alphanumeric space , _ - # and . are allowed.'

                        # Return custom portfolio name
                        else:
                            return other

                # Cancel
                else:
                    return False

            # Existing portfolio
            if choice < otherIndex:
                return folios[choice - 1]

        except Exception as e:
            self.logger.error(e)

    def show_summary(self, title='Summary'):
        """
        Show a summary of the settings that will be used for auto investing
        """

        print '\n========= {0} ========='.format(title)
        print 'Invest ALL available funds with the following criteria\n'
        print 'With at LEAST ${0} available to invest'.format(self.settings['minCash'])
        print 'Select a portfolio with an average interest rate between {0}% - {1}%'.format(self.settings['minPercent'], self.settings['maxPercent'])

        if self.settings['portfolio']:
            print 'Add investments to: "{0}"'.format(self.settings['portfolio'])

        # Filters
        if self.settings['filters'] is not False:
            print '\nAdvanced filters:'

            # Exclude existing
            if self.settings['filters']['exclude_existing']:
                print '  + Exclude loans already invested in'

            # Loan term
            terms = []
            if 'term36month' in self.settings['filters'] and self.settings['filters']['term36month']:
                terms.append('36')
            if 'term60month' in self.settings['filters'] and self.settings['filters']['term60month']:
                terms.append('60')
            print '  + Term: {0} months'.format(' & '.join(terms))

            # Interest rate grades
            if self.settings['filters']['grades']['All']:
                print '   + All interest rate grades'
            else:
                grades = []
                for grade in self.settings['filters']['grades']:
                    if grade != 'All' and self.settings['filters']['grades'][grade] is True:
                        grades.append(grade)
                print '  + Interest rates grades: {0}'.format(', '.join(sorted(grades)))

        print '=========={0}==========\n'.format(''.center(len(title), '='))

    def get_investment_settings(self):
        """
        Show the user a series of prompts to determine how they want the tool to automatically invest.
        This fills out the settings dictionary.
        """

         # Minimum cash
        print '---------'
        print 'The auto investor will automatically try to invest ALL available cash into a diversified portfolio'
        while(True):
            self.settings['minCash'] = self.prompt_int('What\'s the MINIMUM amount of cash you want to invest each round?', self.settings['minCash'])
            if self.settings['minCash'] < 25:
                print '\nYou cannot invest less than $25. Please try again.'
            else:
                break

        # Min/max percent
        print '---------'
        while(True):
            print 'When auto investing, the LendingClub API will provide us a list of possible investment portfolios available at that moment.'
            print 'To pick the appropriate one for you, it needs to know what the minimum and maximum AVERAGE interest rate value you will accept.'
            print 'The investment option closest to the maximum value will be chosen and all your available cash will be invested in it.\n'

            self.settings['minPercent'] = self.prompt_float('What\'s MININUM average interest rate portfolio that you will accept?', self.settings['minPercent'])

            # Max percent should default to being larger than the min percent
            if self.settings['maxPercent'] is False or self.settings['maxPercent'] < self.settings['minPercent']:
                self.settings['maxPercent'] = self.settings['minPercent'] + 1
            self.settings['maxPercent'] = self.prompt_float('What\'s MAXIMUM average interest rate portfolio that you will accept?', self.settings['maxPercent'])

            # Validation
            if self.settings['maxPercent'] < self.settings['minPercent']:
                print 'The maximum value must be larger than, or equal to, the minimum value. Please try again.'
            elif self.settings['maxPercent'] == self.settings['minPercent']:
                print 'It\'s very uncommon to find an available portfolio that will match an exact percent.'
                if not self.prompt_yn('Would you like to specify a broader range?'):
                    break
            else:
                break

        # Portfolio
        print '---------'
        folioOption = False
        if self.settings['portfolio']:  # if saved settings has a portfolio set, default the prompt to 'Y' to choose
            folioOption = 'y'

        if self.prompt_yn('Do you want to put your new investments into a named portfolio?', folioOption):
            self.settings['portfolio'] = self.portfolio_picker(self.settings['portfolio'])
        else:
            self.settings['portfolio'] = False

        # Advanced filter settings
        print '\n---------'
        if self.prompt_yn('Would you like to set advanced filter settings?', self.settings['filters'] is not False):
            self.get_filter_settings()

        # Review summary
        self.show_summary()
        if self.prompt_yn('Would you like to continue with these settings?', 'y'):
            self.save_settings()
        else:
            self.get_investment_settings()

        return True

    def get_filter_settings(self):
        filters = self.settings['filters']
        if not filters:
            filters = {
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

        print 'The following questions are from the filters section of the Invest page on LendingClub\n'

        filters['exclude_existing'] = self.prompt_yn('Exclude loans already invested in?', filters['exclude_existing'])

        print '---------'
        print 'Choose term (36 - 60 month)'

        while(True):
            filters['term36month'] = self.prompt_yn('Include 36 month term loans?', filters['term36month'])
            filters['term60month'] = self.prompt_yn('Include 60 month term loans?', filters['term60month'])

            # Validate 1 was chosen
            if not filters['term36month'] and not filters['term60month']:
                print 'You have to AT LEAST choose one term length!'
            else:
                break

        print '---------'
        print 'Choose interest rate grades (7.4% - 24.84%)'
        while(True):
            if self.prompt_yn('Include ALL interest rate grades', filters['grades']['All']):
                filters['grades']['All'] = True
            else:
                filters['grades']['All'] = False
                filters['grades']['A'] = self.prompt_yn('A - ~7.41%', filters['grades']['A'])
                filters['grades']['B'] = self.prompt_yn('B - ~12.12%', filters['grades']['B'])
                filters['grades']['C'] = self.prompt_yn('C - ~15.80%', filters['grades']['C'])
                filters['grades']['D'] = self.prompt_yn('D - ~18.76%', filters['grades']['D'])
                filters['grades']['E'] = self.prompt_yn('E - ~21.49%', filters['grades']['E'])
                filters['grades']['F'] = self.prompt_yn('F - ~23.49%', filters['grades']['F'])
                filters['grades']['G'] = self.prompt_yn('G - ~24.84%', filters['grades']['G'])

            # Verify one was chosen
            gradeChosen = False
            for grade in filters['grades']:
                if filters['grades'][grade] is True:
                    gradeChosen = True
            if not gradeChosen:
                print 'You have to AT LEAST choose one interest rate grade!'
            else:
                break

        self.settings['filters'] = filters

    def get_auth_settings(self):
        """
        Get the initial settings for the funder
        """

        # Authenticate
        print 'To start, we need to log you into Lending Club (your password will never be saved)\n'
        while(True):
            self.settings['email'] = self.prompt('LendingClub email', self.settings['email'])
            self.settings['pass'] = self.get_password()

            print '\nAuthenticating...'
            if self.authenticate():
                break
            else:
                print "\nCould not authenticate, please try again"

        print 'Success!\n'
        print 'You have ${0} in your account, free to invest\n'.format(self.get_cash_balance())
        return True


class AutoInvestorError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
