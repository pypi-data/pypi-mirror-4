""" View
"""
import logging
import urllib2
from urllib import quote
from urllib import urlencode
from zope.component import queryUtility
import json as simplejson
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from collective.diffbot.interfaces import IDiffbotSettings
from collective.diffbot.cache import ramcache, cacheJsonKey

logger = logging.getLogger('collective.diffbot')

class Diffbot(BrowserView):
    """ Diffbot
    """
    def __init__(self, context, request):
        super(Diffbot, self).__init__(context, request)
        self._settings = None

    @property
    def headers(self):
        """ Headers
        """
        return {
            'User-Agent' : 'collective.diffbot'
        }

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            self._settings = queryUtility(
                IRegistry).forInterface(IDiffbotSettings, False)
        return self._settings

    @ramcache(cacheJsonKey, dependencies=['collective.diffbot'])
    def json(self, **kwargs):
        """ Get JSON from diffbot
        """
        res = {}
        url = self.request.form.get('url', None)
        if not url:
            logger.warn("Invalid url provided %s", url)
            return simplejson.dumps(res)

        diffbot = self.settings.url
        token = self.settings.token

        query = urlencode(dict(token=token, url=url))
        try:
            # XXX
            #request = urllib2.Request(diffbot, query, headers=self.headers)
            conn = urllib2.urlopen(diffbot + "?" + query)
        except Exception, err:
            logger.exception(err)
            return simplejson.dumps(res)
        else:
            return conn.read()
        finally:
            conn.close()
