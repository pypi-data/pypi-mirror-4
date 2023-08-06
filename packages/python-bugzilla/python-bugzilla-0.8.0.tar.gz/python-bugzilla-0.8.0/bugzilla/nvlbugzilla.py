# nvlbugzilla.py - a Python interface to Novell Bugzilla using xmlrpclib.
#
# Copyright (C) 2009 Novell Inc.
# Author: Michal Vyskocil <mvyskocil@suse.cz>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import cookielib
import os
import re
import time
import urllib
import urllib2
import urlparse

from bugzilla import BugzillaError, Bugzilla34, log


class NovellBugzilla(Bugzilla34):
    '''
    bugzilla.novell.com is a standard bugzilla 3.2 with some extensions, but
    it uses an proprietary and non-standard IChain login system. This class
    reimplements a login method which is compatible with iChain.

    Because login process takes relativelly long time, because it needs several
    HTTP requests,  NovellBugzilla caches the session cookies of bugzilla
    and IChain in a self._cookiefile to speedup a repeated connections.
    To avoid problems with cookie expiration, it set the expiration of cookie
    to 5 minutes. This expects cookies stored in LWPCookieJar format and
    login method warn if cookies are in MozillaCookieJar format.

    It can also read a credentials from ~/.oscrc if exists, so it should not
    be duplicated in /etc/bugzillarc, or ~/.bugzillarc.
    '''

    version = '0.1'

    bnc_cookie_re = re.compile('^Z.*-bugzilla')
    ichain_cookie_re = re.compile('^IPC.*')
    # pylint: disable=W1401
    # Anomolous backslash in string
    cookie_domain_re = re.compile('.*\.novell\.com$')
    # pylint: enable=W1401

    bugzilla_url = 'https://bugzilla.novell.com/xmlrpc.cgi'
    logout_url = 'https://www.novell.com/cmd/ICSLogout'
    obs_url = 'https://api.opensuse.org/'
    login_path = '/index.cgi?GoAheadAndLogIn=1'
    auth_path = '/ICSLogin/auth-up'
    ichainlogin_path = '/ichainlogin.cgi'

    def __init__(self, expires=300, **kwargs):
        self._expires = expires
        self._url = self.__class__.bugzilla_url
        self._opener = None

        # url argument exists only for backward compatibility,
        # but is always set to same url
        super(NovellBugzilla, self).__init__(**kwargs)

    def __get_expiration(self):
        return self._expires

    def __set_expiration(self, expires):
        self._expires = expires

    expires = property(__get_expiration, __set_expiration)

    def _iter_domain_cookies(self):
        '''
        Return an generator from all cookies matched a
        self.__class__.cookie_domain_re
        '''
        return (c for c in self._cookiejar if
                self.__class__.cookie_domain_re.match(c.domain) and
                not c.is_expired())

    def _is_bugzilla_cookie(self):
        return len([c for c in self._iter_domain_cookies() if
                   self.__class__.bnc_cookie_re.match(c.name)]) != 0

    def _is_ichain_cookie(self):
        return len([c for c in self._iter_domain_cookies() if
                    self.__class__.ichain_cookie_re.match(c.name)]) != 0

    def _is_lwp_format(self):
        return isinstance(self._cookiejar, cookielib.LWPCookieJar)

    def _login(self, user, password):
        cls = self.__class__

        # remove /xmlrpc.cgi
        base_url = self.url[:-11]

        lwp_format = self._is_lwp_format()
        if not lwp_format:
            log.warn("File `%s' is not in LWP format required for "
                     "NovellBugzilla. If you want cache the cookies "
                     "and speedup the repeated connections, remove it "
                     "or use an another file for cookies.", self._cookiefile)

        if lwp_format and not self._is_bugzilla_cookie():
            login_url = urlparse.urljoin(base_url, cls.login_path)
            log.info("GET %s" % login_url)
            login_resp = self._opener.open(login_url)
            if login_resp.code != 200:
                raise BugzillaError("The login failed with code %d" %
                                    login_resp.core)

        params = {
            'url': urlparse.urljoin(base_url, cls.ichainlogin_path),
            'target': cls.login_path[1:],
            'context': 'default',
            'proxypath': 'reverse',
            'nlogin_submit_btn': 'Log In',
            'username': user,
            'password': password,
        }

        if lwp_format and not self._is_ichain_cookie():
            auth_url = urlparse.urljoin(base_url, cls.auth_path)
            auth_params = urllib.urlencode(params)
            auth_req = urllib2.Request(auth_url, auth_params)
            log.info("POST %s" % auth_url)
            auth_resp = self._opener.open(auth_req)
            if auth_resp.code != 200:
                raise BugzillaError("The auth failed with code %d" %
                                    auth_resp.core)

        if lwp_format:
            for cookie in self._cookiejar:
                # expires cookie in 15 minutes
                cookie.expires = time.time() + self._expires
                cookie.discard = False

        return super(NovellBugzilla, self)._login(user, password)

    def connect(self, url):
        # NovellBugzilla should connect only to bnc

        handler = urllib2.HTTPCookieProcessor(self._cookiejar)
        self._opener = urllib2.build_opener(handler)
        self._opener.addheaders = [('User-agent', self.user_agent)]

        return super(NovellBugzilla, self).connect(self.__class__.bugzilla_url)

    def _logout(self):
        '''Novell bugzilla don't support xmlrpc logout, so let's implement it.
        This method also set all domain cookies as expired.
        '''
        self._opener.open(self.__class__.logout_url)
        # expire cookies
        for cookie in self._iter_domain_cookies():
            cookie.expires = 0

    def readconfig(self, configpath=None):
        super(NovellBugzilla, self).readconfig(configpath)

        oscrc = os.path.expanduser('~/.oscrc')
        if (not self.user and
            not self.password and
            os.path.exists(oscrc)):

            from ConfigParser import SafeConfigParser, NoOptionError
            c = SafeConfigParser()
            r = c.read(oscrc)
            if not r:
                return

            obs_url = self.__class__.obs_url
            if not c.has_section(obs_url):
                return

            try:
                self.user = c.get(obs_url, 'user')
                self.password = c.get(obs_url, 'pass')
                log.info("Read credentials from ~/.oscrc")
            except NoOptionError:
                return
