from zope.interface import Interface

# -*- extra stuff goes here -*-
from blogentry import IBlogEntry
from blog import IBlog

class IProductLayer(Interface):
    """ A layer specific to this product.
        Is registered using browserlayer.xml
    """
