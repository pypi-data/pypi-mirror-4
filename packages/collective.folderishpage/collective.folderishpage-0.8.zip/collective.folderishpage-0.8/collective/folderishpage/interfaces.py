from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.folderishpage import folderishpageMessageFactory as _

class IATFolderishDocument(Interface):
    """A page in the site. Can contain rich text."""
