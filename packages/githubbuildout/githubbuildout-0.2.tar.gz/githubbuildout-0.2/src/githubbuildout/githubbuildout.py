##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


import urllib2
import os
import csv
import logging
import subprocess
import urllib
from StringIO import StringIO
from zc.buildout import download
import urlparse


log = logging.getLogger('githubbuildout')


def get_github_credentials():
    """
    Returns the credentials for the local git installation by using
    `git config` command line.
    """
    log.debug("Getting github credentials")
    p = subprocess.Popen("git config github.accesstoken", shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rc = p.wait()
    if rc:
        log.warn("Failed to get github credentials")
        return None # failure to get config, so return silently

    token = p.stdout.readline().strip()
    if token:
        log.debug("Found GitHub authorization token %r", token)
        return token
    else:
        log.warn("Could not find GitHub authorization token "
                "(\"github.accesstoken\"). Has one been defined?")


def handle_github_url(full_url, extra_query=None):
    """
    Parses the request object and returns the 'correct' URL to retrieve the
    requested data from GitHub as a string.

    In the event that the URL does not conform to one of the supported
    URL formats, 'Nonetype' will be returned, in which case you should
    probably not attempt to open the URL using the access token.
    """
    # Dissect the URL into component parts
    scheme, netloc, path,\
    params, query, fragment = urlparse.urlparse(full_url)

    # Handle 'end-user' GitHub URLs
    path_parts = [x for x in path.split('/') if x]
    if netloc in ['github.com', 'www.github.com']:
        if 'downloads' in path_parts:
            log.debug("GitHub static file download URL %r found"
                      % (full_url,))
        elif 'zipball' in path_parts or 'tarball' in path_parts:
            log.debug("GitHub repository download URL %r found"
                      % (full_url,))

            # Rewrite netloc/path to use API v3 for request
            netloc = 'api.github.com'
            path = 'repos/%s' % (path.lstrip('/'),)

        else:
            errmsg = "GitHub URL %r is not a supported " \
                     "URL for this extension" % (full_url,)
            log.debug(errmsg)
            return None

    # Handle 'API' GitHub URLs
    elif netloc in ['api.github.com']:
        log.debug("GitHub API server URL %r found" % (full_url,))
        pass

    # Include passed extra_query parameters if present
    if extra_query:
        extra_params = urllib.urlencode(extra_query)
        query = '&'.join((query, extra_params))

    # Reassemble the URL and return
    new_url = urlparse.urlunparse((scheme, netloc, path,
                                   params, query, fragment))
    return new_url


class GithubHandler(urllib2.BaseHandler):
    """
    Handles GitHub requests when the protocol is https (only). http protocol
    requests are not handled.
    """

    def __init__(self, token):
        """
        Create a new GithubHandler instance. Requires a pre-created GitHub
        API v3 authorization token; see README.rst for details.

        @token: A 40-character hexadecimal string representing a valid GitHub
                API v3 authorization token with access to the requested URL
        """
        self._token = token

    def https_request(self, req):
        """
        Implements an alternative request handler for https-based requests:

        * Rewrites the hostname and path to use the GitHub API server if you
          appear to be requesting a repository;

        * Uses the hostname/path as-is if you are downloading a static file,
          or if you are already using the GitHub API server in your URL

        @req: The urllib2 Request instance
        """
        if req.get_method() is not 'GET':
            log.warn("Only 'GET' method is supported, got %r instead" %
                      (req.get_method,))
            pass
        else:
            # Retrieve the original request's timeout, default to 30 (secs.)
            timeout = getattr(req, 'timeout', 30)

            # Fetch the correct URL to use; return immediately if None
            new_url = handle_github_url(req.get_full_url())
            if not new_url:
                return req

            # Set the Authorization token in the request headers.
            # Since 2013-04-24, the user agent must be declared:
            # http://developer.github.com/changes/
            # 2013-04-24-user-agent-required/
            headers = {
                'Authorization': 'token %s' % (self._token,),
                'User-Agent': 'githubbuildout/0.2 zc.buildout',
            }
            log.debug("Adding GitHub authorization token to header")

            req = urllib2.Request(new_url, headers=headers)
            req.timeout = timeout

        return req


class URLOpener(download.URLOpener):
    """
    Custom URL Opener for handling GitHub credentials when downloading
    URLs using openers based on zc.buildout.download (e.g.
    hexagonit.recipe.download).
    """

    def __init__(self, token):
        """
        Create a new GitHub-enabled URLOpener instance.

        @token: A valid API v3 authorization token for the URL(s) you
                intend to retrieve (40-char string).
        """
        self._token = token
        download.URLOpener.__init__(self)

    def retrieve(self, url, filename=None, reporthook=None, data=None):
        """
        Implements the retrieve method; please see the parent method for
        details.
        """
        if self._token and not data:
            new_url = handle_github_url(url, {'access_token': self._token})
            if new_url:
                url = new_url
                log.debug("Added GitHub authorization token to request")

        return download.URLOpener.retrieve(self, url, filename,
                                           reporthook, data)


def install(buildout=None):
    """
    The main entry-point for this application; called when buildout executes.
    """
    github_creds = get_github_credentials()
    if github_creds:
        new_handlers = list()
        new_handlers.append(GithubHandler(github_creds))
        download.url_opener = URLOpener(github_creds)
        if urllib2._opener is not None:
            handlers = urllib2._opener.handlers[:]
            handlers[:0] = new_handlers
        else:
            handlers = new_handlers
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)

