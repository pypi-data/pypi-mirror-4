# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from collective.taxonomysupport.interfaces import ITaxonomyLevel
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import alsoProvides, noLongerProvides

from collective.taxonomysupport import taxonomysupportMessageFactory as _

class CheckTaxonomyAction(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_canonical(self):
        pcs = self.context.restrictedTraverse('@@plone_context_state')
        return pcs.canonical_object()

    def check_taxonomy_action_add(self):
        obj = self.get_canonical()
        return not ITaxonomyLevel.providedBy(obj)

    def check_taxonomy_action_remove(self):
        obj = self.get_canonical()
        return ITaxonomyLevel.providedBy(obj)


class ToggleMarkTaxonomyRoot(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_canonical(self):
        pcs = self.context.restrictedTraverse('@@plone_context_state')
        return pcs.canonical_object()

    def add_interface(self):
        obj = self.get_canonical()
        messages = IStatusMessage(self.request)
        if not ITaxonomyLevel.providedBy(obj):
            alsoProvides(obj, ITaxonomyLevel)
            obj.reindexObject()
            messages.addStatusMessage(_('label_content_marked_as_taxonomyroot',
                                        default=u"Content marked as taxonomy root"),
                                      type='info')
        else:
            messages.addStatusMessage(_('label_content_already_taxonomyroot',
                                        default=u"Content already marked as taxonomy root"),
                                      type='warning')
        self.request.response.redirect(obj.absolute_url())

    def remove_interface(self):
        obj = self.get_canonical()
        messages = IStatusMessage(self.request)
        if ITaxonomyLevel.providedBy(obj):
            noLongerProvides(obj, ITaxonomyLevel)
            obj.reindexObject()
            messages.addStatusMessage(_('label_content_unmarked_as_taxonomyroot',
                                        default=u"Content unmarked as taxonomy root"),
                                      type='info')
        else:
            messages.addStatusMessage(_('label_content_already_unmarked_taxonomyroot',
                                        default=u"Content was not marked as taxonomy root"),
                                      type='warning')
        self.request.response.redirect(obj.absolute_url())
