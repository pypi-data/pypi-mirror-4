"""Definition of the Map content type
"""
from zope.interface import implements
from AccessControl import ClassSecurityInfo

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

try: # Plone 4 and higher
    from archetypes.referencebrowserwidget import ReferenceBrowserWidget
except: # BBB Plone 3
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from raptus.article.alias.interfaces import IAlias
from raptus.article.alias.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core.componentselection import ComponentSelectionWidget


AliasSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
        atapi.ReferenceField('reference',
            relationship = 'aliasTo',
            allowed_types_method = 'getAllowedTypes',
            multiValued = False,
            required = True,
            keepReferencesOnCopy = True,
            widget = ReferenceBrowserWidget(
                allow_search = True,
                allow_browse = True,
                show_indexes = False,
                force_close_on_insert = True,
                label = _(u'label_reference', default=u'Reference'),
                description = '',
                visible = {'edit' : 'visible', 'view' : 'invisible' }
            )
        ),
        atapi.LinesField('components',
            enforceVocabulary = True,
            vocabulary_factory = 'componentselectionvocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = ComponentSelectionWidget(
                description = _(u'description_component_selection_alias', default=u'Select the components in which the referenced object should be displayed.'),
                label= _(u'label_component_selection', default=u'Component selection'),
            )
        ),
    ))

AliasSchema['title'].required = False

for field in ('title', 'description', 'creators', 'allowDiscussion', 'contributors', 'location', 'language', 'nextPreviousEnabled', 'rights', 'excludeFromNav', 'subject', 'relatedItems'):
    if AliasSchema.has_key(field):
        AliasSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(AliasSchema, folderish=False, moveDiscussion=True)

class Alias(base.ATCTContent):
    """An alias"""
    implements(IAlias)
    
    portal_type = "Alias"
    schema = AliasSchema

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'Title')
    def Title(self):
        """Returns the title of the referenced object
        """
        ref = self.getReference()
        return ref.Title() if ref is not None else ''

    security.declareProtected(permissions.View, 'Description')
    def Description(self):
        """Returns the description of the referenced object
        """
        ref = self.getReference()
        return ref.Description() if ref is not None else ''

    def getAllowedTypes(self):
        return getToolByName(self, 'portal_types')._getOb('Article').getProperty('allowed_content_types', [])

atapi.registerType(Alias, PROJECTNAME)
