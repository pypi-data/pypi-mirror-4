"""Definition of the Suite content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from adi.suite.interfaces import ISuite
from adi.suite.config import PROJECTNAME

from Products.Archetypes.atapi import *

from Products.ATContentTypes import ATCTMessageFactory as _

SuiteSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    TextField('adinfo',
        required = False,
        searchable = True,
        primary = True,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = RichWidget(
            description = '',
            label = _(u'label_body_text', u'Body Text'),
            rows = 27,
            allow_file_upload = True)
        ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SuiteSchema['title'].storage = atapi.AnnotationStorage()
SuiteSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    SuiteSchema,
    folderish=True,
    moveDiscussion=False
)


class Suite(folder.ATFolder):
    """A container for javascript popup galleries."""
    implements(ISuite)

    meta_type = "Suite"
    schema = SuiteSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Suite, PROJECTNAME)
