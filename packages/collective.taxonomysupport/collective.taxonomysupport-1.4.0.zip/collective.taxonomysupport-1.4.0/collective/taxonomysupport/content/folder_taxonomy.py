"""Definition of the Folder for news content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from collective.taxonomysupport.config import PROJECTNAME
from collective.taxonomysupport.interfaces import IFolderTaxonomy
from zope.interface import implements

class FolderTaxonomy(folder.ATFolder):
    """Folder for taxonomy"""
    implements(IFolderTaxonomy)

    meta_type = "FolderTaxonomy"

registerATCT(FolderTaxonomy, PROJECTNAME)
