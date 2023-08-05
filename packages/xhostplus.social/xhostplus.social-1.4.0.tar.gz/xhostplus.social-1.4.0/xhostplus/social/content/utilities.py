# -*- coding: utf-8 -*-

"""Utilities to store the settings
"""

from zope.interface import implements
from zope.component import getUtility
from zope.schema.fieldproperty import FieldProperty
from xhostplus.social.interfaces.configuration import ISocialConfiguration

from OFS.SimpleItem import SimpleItem

def social_configuration_adapter(context):
    return getUtility(ISocialConfiguration, context=context)

class SocialConfiguration(SimpleItem):
    implements(ISocialConfiguration)

    two_click_buttons = FieldProperty(ISocialConfiguration['two_click_buttons'])

    enable_facebook = FieldProperty(ISocialConfiguration['enable_facebook'])
    enable_gplus = FieldProperty(ISocialConfiguration['enable_gplus'])
    enable_twitter = FieldProperty(ISocialConfiguration['enable_twitter'])
    enable_linkedin = FieldProperty(ISocialConfiguration['enable_linkedin'])

    twitter_hashtags = FieldProperty(ISocialConfiguration['twitter_hashtags'])
