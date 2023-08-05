# -*- coding: utf-8 -*-

from collective.taxonomysupport.interfaces import ITaxonomyLayer
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_chain
from collective.taxonomysupport.interfaces import IFolderTaxonomy

def getDefaultTaxonomy(self):
    if not self.REQUEST.__provides__(ITaxonomyLayer):
        return ''

    vocab=queryUtility(IVocabularyFactory,name='collective.taxonomyvocab')
    list_taxonomies=vocab(self)
    if not list_taxonomies:
        return ''
    taxonomy_folder=[x for x in self.getFolderWhenPortalFactory().aq_chain if IFolderTaxonomy.providedBy(x)]
    if not taxonomy_folder:
        return ''
    for elem in list_taxonomies:
        if elem.value == taxonomy_folder[0].UID():
            return elem.value
    return ''

def getSiteAreas(self):
    """Generated accessor"""
    return self.getRawSiteAreas()

def getRawSiteAreas(self):
    """Generated raw accessor"""
    if not self.REQUEST.__provides__(ITaxonomyLayer):
        return ()

    if not self.getField('siteAreas'):
        return tuple()
    siteAreas = list(self.getField('siteAreas').get(self))
    for parent in aq_chain(self):
        if IFolderTaxonomy.providedBy(parent):
            siteAreas.append(parent.UID())
    return tuple(set(siteAreas))

def SiteAreas(self):
    """Generated indexes; show all available site areas"""
    if not self.REQUEST.__provides__(ITaxonomyLayer):
        return ()

    portal_catalog=getToolByName(self,'portal_catalog')
    areas = self.getRawSiteAreas()
    if not areas:
        return ()
    listtitle = []
    results = portal_catalog.searchResults(UID=areas)
    if results:
        listtitle.extend([x.Title for x in results])
    return tuple(listtitle)

def showAreas(self):
    if not self.REQUEST.__provides__(ITaxonomyLayer):
        return ''

    vocab=queryUtility(IVocabularyFactory, name='collective.taxonomyvocab')
    if not vocab(self):
        return False
    return True

