# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

try:
    import json
except ImportError:
    import simplejson as json

class DataGridAutocompleteView(BrowserView):
    """Return a search on the site for referenced objects
    
    It commonly return a JSON with results
    
    The view need a "term" parameter
    
    An optional "origin" parameter can give to the view the traversal path of the calling context
    
    """
    
    def __call__(self, *args, **kw):
        context = self.context
        request = self.request
        response = request.response
        catalog = getToolByName(context, 'portal_catalog')

        response.setHeader('Content-Type','application/json')
        response.addHeader("Cache-Control", "no-cache")
        response.addHeader("Pragma", "no-cache")

        term = request.get('term', '').lstrip()
        object_provides = request.get('object_provides')
        search_site = request.get('search_site')
        surf_site = request.get('surf_site')
        
        # PATH search
        if term.startswith('/') and surf_site:
            portal = getToolByName(context, 'portal_url').getPortalObject()
            terms = term.split('/')
            searchPath = '/' + portal.getId() + '/'.join(terms[:-1])
            lastTerm = terms[-1]
            results = catalog(path={'query': searchPath, 'depth': 1},
                              sort_on='getObjPositionInParent')
            return json.dumps([{'label': x.Title,
                                'value': x.UID,
                                'path': x.getPath()} for x in results if \
                        x.getId.startswith(lastTerm) or x.Title.startswith(lastTerm)
                    ])
        # FULLTEXT search
        elif term and search_site: # term must be something
            terms = term.strip().split()
            path = '/'.join(context.getPhysicalPath())
            kwargs = {'Title': ' AND '.join(["%s*" % x for x in terms]),
                      'sort_on': 'sortable_title',
                      'sort_order': 'reverse',
                      'path': path}
            if object_provides:
                kwargs['object_provides'] = object_provides
            results = catalog(**kwargs)
            return json.dumps([{'label': x.Title,
                                'value': x.UID,
                                'path': x.getPath()} for x in results])
        return json.dumps([])
        