"""Definition of the Press Kit content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.pressKit.interfaces import IPressKit
from Products.pressKit.config import PROJECTNAME

PressKitSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PressKitSchema['title'].storage = atapi.AnnotationStorage()
PressKitSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PressKitSchema,
    folderish=True,
    moveDiscussion=False
)


class PressKit(folder.ATFolder):
    """Folder that holds press documents downloadable as a zip bundle."""
    implements(IPressKit)

    meta_type = "PressKit"
    schema = PressKitSchema
    schema['relatedItems'].widget.visible['edit'] = 'visible'

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(PressKit, PROJECTNAME)
