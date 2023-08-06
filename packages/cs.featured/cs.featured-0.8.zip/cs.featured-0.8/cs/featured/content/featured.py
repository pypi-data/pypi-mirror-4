"""Definition of the featured content type
"""
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi


from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import newsitem

from cs.featured import featuredMessageFactory as _
from cs.featured.interfaces import Ifeatured
from cs.featured.config import PROJECTNAME

featuredSchema = newsitem.ATNewsItemSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

        atapi.StringField('Link',
                          required=True,
                          searchable=True,
                          languageIndependent=False,
                          storage=atapi.AnnotationStorage(),
                          widget=atapi.StringWidget(label=_(u'Linka'),
                                                    size=40,
                                                    ),
                          ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

featuredSchema['title'].storage = atapi.AnnotationStorage()
featuredSchema['description'].storage = atapi.AnnotationStorage()

featuredSchema['description'].widget.visible['edit']='invisible'
featuredSchema['description'].widget.visible['view']='invisible'

featuredSchema['imageCaption'].widget.visible['edit']='invisible'
featuredSchema['imageCaption'].widget.visible['view']='invisible'



schemata.finalizeATCTSchema(featuredSchema, moveDiscussion=False)

class featured(newsitem.ATNewsItem):
    """Description of Featured"""
    implements(Ifeatured)

    portal_type = "featured"
    schema = featuredSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(featured, PROJECTNAME)
