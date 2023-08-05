# -*- coding: utf-8 -*-

try:
    # python2.6
    import json
except ImportError:
    # python2.4
    import simplejson as json

from plone.memoize.instance import memoize
from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IImageContent


class QueryImagesView(BrowserView):
    """Query all image and image-like contents from a Collection

    return a JSON structure like this:

    {'title': the title of the Plone content,
     'url': URL to the content
     'type': type of content
     'description': description of the content
     }

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kw):
        response = self.request.response
        response.setHeader('content-type', 'application/json')
        #response.addHeader("Cache-Control", "no-cache")
        #response.addHeader("Pragma", "no-cache")
        results = self._results
        images = []
        for x in results:
            images.append({'title': x.Title,
                           'url': x.getURL(),
                           'type': x.portal_type,
                           'description': x.Description,
                           })
        return json.dumps(images)

    @property
    @memoize
    def _results(self):
        topic = self.context
        self.request.set('object_provides', IImageContent.__identifier__)
        try:
            #Old Topics
            results = topic.queryCatalog(object_provides=IImageContent.__identifier__)
        except TypeError:
            #New collections
            results = topic.queryCatalog()
        return results
