# -*- coding: utf-8 -*-

from zope.schema.vocabulary import SimpleTerm
from Products.CMFPlone.utils import getToolByName
from collective.taxonomysupport.interfaces import ITaxonomyLevel, IFolderTaxonomy

def taxonomyvocab(context):
    """
    Return a vocabulary with a list of availables taxonomies
    """
    pc=getToolByName(context,'portal_catalog')
    interface_name=ITaxonomyLevel.__identifier__
    #a list of all activated sections in the site
    activated_sections=pc(object_provides = interface_name)
    #set of activated parents of the current object 
    parent_sections=set()
    #a list of activated paths
    activated_paths=set()
    obj_path='/'.join(context.getFolderWhenPortalFactory().getPhysicalPath())
    for section in activated_sections:
        activated_paths.add(section.getPath())
        if obj_path.startswith(section.getPath()):
            parent_sections.add(section.getPath())
    if not parent_sections:
        #no one activated section in the tree of current object
        root=context.portal_url.getPortalObject()
        if not ITaxonomyLevel.providedBy(root):
            return []
        parent_sections.add('/'.join(root.getPhysicalPath()))
        
    first_activated_parent=max(parent_sections)
    taxonomies=pc(object_provides=IFolderTaxonomy.__identifier__,
                  path=first_activated_parent,
                  sort_on="sortable_title")
    if not taxonomies:
        return []
    terms=[]
    activated_paths.difference_update(parent_sections)
    for elem in taxonomies:
        #this check remove the parent taxonomy from the list, if it's activated
        if elem.getPath() == first_activated_parent:
            continue
        #this check remove all the blocked taxonomies from the list
        if isBlocked(elem.getPath(),activated_paths):
            continue
        terms.append(SimpleTerm(value=elem.UID, token=elem.UID, title=elem.Title))
    return terms

def isBlocked(item_path,list_paths):
    """
    Check if the passed path is a child of some blocked sections
    """
    for path in list_paths:
        if item_path.startswith(path) and not item_path == path:
            return True
    return False
