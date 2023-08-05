from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes.public import BooleanWidget, StringWidget
from Products.ATContentTypes.interface.interfaces import IATContentType
from Products.Archetypes.public import BooleanField, StringField

from xhostplus.social import socialMessageFactory as _
from xhostplus.social.interfaces import IProductLayer

ToggleSocialButtonsPermission = 'xhostplus.social: Toggle social-buttons option'
EditTwitterHashtagsPermission = 'xhostplus.social: Edit Twitter hashtags'

class SocialBooleanField(ExtensionField, BooleanField):
    """Toggle button for enabling social buttons."""

class TwitterHashtagsField(ExtensionField, StringField):
    """Twitter hashtags for a page."""

class BaseExtender(object):
    adapts(IATContentType)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IProductLayer

    fields = [
        SocialBooleanField("socialButtons",
            languageIndependent=1,
            default=True,
            schemata='settings',
            widget = BooleanWidget(
                description=_(u'help_social_buttons', default=u'If selected, this item will show social buttons on the bottom of the content.'),
                label = _(u'label_social_buttons', default=u'Social buttons'),
                visible={'view' : 'hidden',
                         'edit' : 'visible'},
            ),
            required=False,
            searchable=False,
            write_permission=ToggleSocialButtonsPermission,
        ),

        TwitterHashtagsField("twitterHashtags",
            languageIndependent=1,
            default='',
            schemata='settings',
            widget = StringWidget(
                description=_(u'help_twitter_hashtags', default=u'Comma-separated list of hashtags that should be added to a tweet for this page.'),
                label = _(u'label_twitter_hashtags', default=u'Twitter Hashtags'),
                visible={'view' : 'hidden',
                         'edit' : 'visible'},
            ),
            required=False,
            searchable=False,
            write_permission=EditTwitterHashtagsPermission,
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
