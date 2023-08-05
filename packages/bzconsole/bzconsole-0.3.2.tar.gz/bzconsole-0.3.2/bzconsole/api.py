"""
console API to bugzilla
"""

import base64
import httplib
import json
import os
import patch
import subprocess
import sys
import urllib
import urllib2

from StringIO import StringIO

from utils import tmpbuffer


class BZapi(object):
    """
    console API to bugzilla
    """

    # currently there is only one cache for configuration
    config_cache = '.bzconfiguration'

    def __init__(self,
                 server='https://api-dev.bugzilla.mozilla.org/latest',
                 refresh=False,
                 print_request=None,
                 username=None,
                 password=None):
        """
        - refresh : refresh the (cached) configuration
        - print_request : log any request information to a file
        """
        self.server = server
        self.refresh = refresh
        self.print_request = print_request
        self.username = username
        self.password = password

    def products(self, classification=None):
        """list bugzilla products"""
        configuration = self.configuration()
        if classification:
            products = [i for i in configuration['product'] if configuration['product'][i]['classification'] == 'Components']
            return sorted(products)
        else:
            return sorted(configuration['product'].keys())

    def components(self, product):
        """list bugzilla components for a particular product"""
        configuration = self.configuration()
        assert product in configuration['product'], 'Product %s not found' % product
        return sorted(configuration['product'][product]['component'].keys())

    def _unique_components(self):
        """returns a dict of unique component, product"""
        retval = {}
        dupe = set()
        for product in self.products():
            for component in self.components(product):
                if component in retval:
                    dupe.add(component)
                else:
                    retval[component] = product
        for d in dupe:
            del retval[d]
        return retval, dupe

    def users(self, match):
        """returns users matching a search string"""
        assert self.username and self.password, "Must be authenticated"
        return self._request('/user?match=%s' % match)

    def bug(self, number):
        """display a bug"""
        number = int(number)
        return self._request('/bug/%d' % number)

    def new(self, component, title, product=None,
            version=None, description=None, whiteboard=(), cc=(),
            blocks=(), depends_on=()):
        """file a new bug. username and password must be set"""

        # sanity check
        if product:
            assert product in self.products(), "Product not found"
            assert component in self.components(product), "Component not found"
        else:
            unique, dupe = self._unique_components()
            assert component in unique, 'Unique component not found: %s' % component
            product = unique[component]
        assert title, 'Must provide a bug summary'
        assert self.username and self.password, "Must be authenticated"

        # infer version if not given
        versions = set(self._configuration['product'][product]['version'])
        if version is None:
            if len(versions) == 1:
                version = list(versions)[0]
            else:
                default_versions = ('unspecified', 'Trunk')
                for ver in default_versions:
                    if ver in versions:
                        version = ver
                        break
        assert version in versions, 'Version not found (Available versions for product "%s": %s)' % (product, versions)

        # create the needed data structure
        request = dict(product=product, component=component,
                       summary=title, version=version,
                       op_sys='All', platform='All',)

        # add CC, if given
        if cc:
            if isinstance(cc, basestring):
                cc=[cc]
            users = []
            for match in cc:
                user = self.users(match)['users']
                assert len(user) == 1, 'Non-unique user: %s' % match
                users.append(user[0])
            request['cc'] = users

        # add blocks, if given:
        if blocks:
            blocks = [int(i) for i in blocks]
            request['blocks'] = blocks

        # add depends_on, if given
        if depends_on:
            depends_on = [int(i) for i in depends_on]
            request['depends_on'] = depends_on

        # get the bug description
        if not description:
            description = tmpbuffer()
        assert description, "Must provide a non-empty description"
        request['comments'] = [self._comment(description)]

        # add whiteboard, if given
        if whiteboard:
            if isinstance(whiteboard, basestring):
                whiteboard=[whiteboard]
            whiteboard = ''.join(['[%s]' % i for i in whiteboard])
            request['whiteboard'] = whiteboard

        # POST the request
        try:
            results = self._request('/bug', request)
        except Exception, e:
            raise

        # return the URL
        return results['ref']

    def attach(self, bug, attachment, description=None, reviewer=None, comment=None):
        """
        add an attachment to a bug

        - bug: bug number to attach to
        - attachment: file or URL of attachment
        - reviewer: flag for review (r?)
        - comment: add this comment to the bug
        """
        # see also:
        # https://github.com/toolness/pybugzilla/blob/master/bzpatch.py

        # TODO: infer bug # from attachment path if possible

        assert self.username and self.password, "Must be authenticated"

        if not description:
            # fairly hacky :/
            description = attachment

        # read contents
        if '://' in attachment:
            # URL
            basename = attachment.rstrip('/').rsplit('/', 1)[-1]
            contents = urllib2.urlopen(attachment).read()
        else:
            # file path
            basename  = os.path.basename(attachment)
            contents = file(attachment).read()

        is_patch = bool(patch.fromstring(contents))
        if is_patch:
            content_type = 'text/plain'
        else:
            # TODO: better content_type
            content_type = 'text/plain'

        # patch flags
        flags = []
        if reviewer:
            # from
            # https://github.com/toolness/pybugzilla/blob/master/bzpatch.py#L177
            flags.append({'name': 'review',
                          'requestee': {'name': reviewer},
                          'status': '?',
                          'type_id': 4 # yay for magic numbers! :/
                          })

        # create attachment data structure
        # https://wiki.mozilla.org/Bugzilla:REST_API:Objects#Attachment
        contents = contents.encode('base64')
        attachment= {'content_type': content_type,
                     'data': contents,
                     'description': description,
                     'encoding': 'base64',
                     'file_name': basename,
                     'flags': flags,
                     'is_patch': is_patch,
                     'is_private': False,
                     'size': len(contents)
                     }

        return self._request('/bug/%s/attachment' % bug, attachment)

    def configuration(self):
        """bugzilla configuration"""

        if not hasattr(self, '_configuration'):
            config_cache = os.path.join(os.environ['HOME'], self.config_cache)
            if not self.refresh:
                try:
                    self._configuration = json.loads(file(config_cache).read())
                except:
                    pass
            if not getattr(self, '_configuration', None):
                self._configuration = self._request('/configuration')
                if not self.print_request:
                    f = file(config_cache, 'w')
                    print >> f, json.dumps(self._configuration)
            self.refresh = False
        return self._configuration

    ### internal methods

    def _comment(self, text):
        retval = {'is_private': False, 'text': text}
        return retval

    def _request(self, path, data=None):
        url = self.server + path
        query = {}
        if self.username:
            query['username'] = self.username
        if self.password:
            query['password'] = self.password
        if query:
            query = urllib.urlencode(query)
            joiner = '?' in url and '&' or '?'
            url += joiner + query
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        if data:
            data = json.dumps(data)
        req = urllib2.Request(url, data, headers)

        # print out the request
        # from http://stackoverflow.com/questions/603856/how-do-you-get-default-headers-in-a-urllib2-request
        if self.print_request:

            f = file(self.print_request, 'a')
            class MyHTTPConnection(httplib.HTTPConnection):
                def send(self, s):
                    print >> f, s  # or save them, or whatever!
                    httplib.HTTPConnection.send(self, s)

            class MyHTTPSConnection(httplib.HTTPSConnection):
                def send(self, s):
                    print >> f, s
                    httplib.HTTPSConnection.send(self, s)

            class MyHTTPHandler(urllib2.HTTPHandler):
                def http_open(self, req):
                    return self.do_open(MyHTTPConnection, req)
            class MyHTTPSHandler(urllib2.HTTPSHandler):
                def https_open(self, req):
                    return self.do_open(MyHTTPSConnection, req)

            if self.server.startswith('https://'):
                opener = urllib2.build_opener(MyHTTPSHandler)
            else:
                opener = urllib2.build_opener(MyHTTPHandler)
            opener.open(req)
            return

        try:
            response = urllib2.urlopen(req)
        except Exception, e:
            print e
            if data:
                print data
            import pdb; pdb.set_trace()
        the_page = response.read()
        return json.loads(the_page)
