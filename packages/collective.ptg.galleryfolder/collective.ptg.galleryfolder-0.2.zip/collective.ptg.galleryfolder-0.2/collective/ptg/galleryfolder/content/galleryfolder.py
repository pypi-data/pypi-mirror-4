"""Definition of the Galleryfolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from collective.ptg.galleryfolder.interfaces import IGalleryfolder
from collective.ptg.galleryfolder.config import PROJECTNAME

GalleryfolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

GalleryfolderSchema['title'].storage = atapi.AnnotationStorage()
GalleryfolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    GalleryfolderSchema,
    folderish=True,
    moveDiscussion=False
)


class Galleryfolder(folder.ATFolder):
    """Gallery Content Type for Plone Truegallery"""
    implements(IGalleryfolder)

    meta_type = "Galleryfolder"
    schema = GalleryfolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Galleryfolder, PROJECTNAME)
