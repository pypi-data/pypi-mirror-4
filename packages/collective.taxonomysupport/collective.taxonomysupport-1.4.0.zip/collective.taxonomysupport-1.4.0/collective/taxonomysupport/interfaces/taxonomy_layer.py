from zope.interface import Interface

class ITaxonomyLayer(Interface):
    """A browser layer for schemaextender"""

class ITaxonomyLevel(Interface):
    """
    This interface can be added manually to some sections of the site, to enable
    the taxonomy  
    """