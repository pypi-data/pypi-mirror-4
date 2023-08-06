import logging

from plone.memoize.instance import memoize
from zope.component import getMultiAdapter, queryMultiAdapter

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
#from Products.CMFCore.WorkflowCore import WorkflowException
#from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import log

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets import ViewletBase

class QRContentRelatedItems(ViewletBase):

    index = ViewPageTemplateFile("document_qrrelateditems.pt")

    def related_items(self):
        context = aq_inner(self.context)
        res = ()
        if base_hasattr(context, 'getRawRelatedItems'):
            catalog = getToolByName(context, 'portal_catalog')
            related = context.getRawRelatedItems()
            if not related:
                return ()
            brains = catalog(UID=related)
            if brains:
                # build a position dict by iterating over the items once
                positions = dict([(v, i) for (i, v) in enumerate(related)])
                # We need to keep the ordering intact
                res = list(brains)
                def _key(brain):
                    return positions.get(brain.UID, -1)
                res.sort(key=_key)
        return res

 
