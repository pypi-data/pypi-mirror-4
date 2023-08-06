"""
    Definition of the ATFolderishDocument content type
"""

from zope.interface import implements
from Products.Archetypes import atapi

# try plone.app.folder first
try:
    from plone.app.folder import folder
except ImportError:
    from Products.ATContentTypes.content import folder

from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.constraintypes \
import ConstrainTypesMixinSchema
from Products.Archetypes.Storage import AttributeStorage
from collective.folderishpage.interfaces import IATFolderishDocument
from collective.folderishpage.config import PROJECTNAME

ATFolderishDocumentSchema = document.ATDocumentSchema.copy()
ATFolderishDocumentSchema += ConstrainTypesMixinSchema.copy()
ATFolderishDocumentSchema += schemata.NextPreviousAwareSchema.copy()
ATFolderishDocumentSchema += atapi.Schema((

))

#folderish=False is intended, because we would like to have relatedItems
# Set text storage to AttributeStorage so we have history diff info
ATFolderishDocumentSchema['text'].storage = AttributeStorage()
schemata.finalizeATCTSchema(ATFolderishDocumentSchema,
                            folderish=False,
                            moveDiscussion=False)


class ATFolderishDocument(folder.ATFolder, document.ATDocument):
    """A page in the site. Can contain rich text."""
    implements(IATFolderishDocument)

    portal_type = "FolderishDocument"
    archetype_name = "Page"
    schema = ATFolderishDocumentSchema

atapi.registerType(ATFolderishDocument, PROJECTNAME)
