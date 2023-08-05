"""Mock Draft Central scraper
"""

import json
import itertools

from lxml import etree, html

import requests

import exceptions


class Scraper(object):
    URLS = {
        'adp': 'http://www.mockdraftcentral.com/report_adp.jsp',
        'auth_step_one': 'http://www.mockdraftcentral.com/login.jsp?sender=index.jsp',
        'auth_step_two': 'http://www.mockdraftcentral.com/login_finish.jsp',
    }

    KEYS = ('rank', 'player', 'position', 'team', 'adp', 'earliest',
            'latest', 'draft_pct', 'taken_in')

    def __init__(self, username, password, sport=1, l_type=280, period=0):
        """Initialize the scraper, set controls to the heart of baseball.
        """

        self._session = requests.session()
        self._results = None

        self.username = username
        self.password = password
        self.sport = sport
        self.l_type = l_type
        self.period = period

    def __iter__(self):
        if self._results is None:
            self._fetch()

        return iter(self._results)

    def _do(self, r_type, url, params=None, data=None, **kwargs):
        return self._session.request(r_type, url,
                                     params=params, data=data,
                                     **kwargs)

    def _auth(self):
        """Authenticate a session with Mock Draft Central.

        Mock Draft Central authentication is a strange dance, in two steps:

        1. POST your credentials to a login resource
        2. Fake automatic resubmission to a "finalization" resource

        """

        def check_response(text):
            """Check to see if authentication has failed.
            """

            if 'incorrect' in response.text:
                msg = ('Username <%(username)s> and password <%(password)s> ' +
                       'do not match.') % {'username': self.username,
                                           'password': self.password}

                raise exceptions.AuthError(msg)

        data = {'action': 'login',
                'user': self.username,
                'pwd': self.password}

        # step 1: submit login form
        response = self._do('POST', self.URLS['auth_step_one'],
                            data=data, allow_redirects=True)
        check_response(response.text)

        # step 2: fake second form's submission
        # todo: sprinkle on some error checking,
        #       even though this is only a redirect
        response = self._do('POST', self.URLS['auth_step_two'],
                            data=data, allow_redirects=True)
        check_response(response.text)

        return True

    def _parse_doc(self, html_doc):
        """Parse the ADP page HTML and iterate out serializable rows.
        """

        c = itertools.count(start=1)

        # load adp page and parse out stats table
        doc = html.fromstring(html_doc)
        rows = doc.xpath(
            '//table[@id="adp_table"]/tr[contains(@class, "contentrow")]')

        for row in rows:
            text = [v.strip() for v in row.xpath('.//text()')[1:]]
            text.insert(0, c.next())
            yield text

    def _fetch(self, output_type='xml'):
        """Fetch MDC page, parse data.
        """

        # authenticate
        self._auth()

        # get the table
        response = self._do('GET', self.URLS['adp'])

        # load results
        self._results = self._parse_doc(response.text)
