# -*- coding: utf-8 -*-

"""Configlet interfaces using zope.formlib
"""

from zope.interface import Interface
from zope import schema

from xhostplus.social import socialMessageFactory as _

class ISocialConfiguration(Interface):

    two_click_buttons = schema.Bool(
        title=_(u"2 click buttons"),
        description=_(u"Enables the 2 click buttons with enhanced privacy."),
        default=False,
        required=True,
    )

    enable_facebook = schema.Bool(
        title=_(u"Facebook"),
        description=_(u"Enables the Facebook button."),
        default=True,
        required=True,
    )

    enable_gplus = schema.Bool(
        title=_(u"Google+"),
        description=_(u"Enables the Google+ button."),
        default=True,
        required=True,
    )

    enable_twitter = schema.Bool(
        title=_(u"Twitter"),
        description=_(u"Enables the Twitter button."),
        default=True,
        required=True,
    )

    enable_linkedin = schema.Bool(
        title=_(u"LinkedIn"),
        description=_(u"Enables the LinkedIn button."),
        default=True,
        required=True,
    )

    twitter_hashtags = schema.TextLine(
        title=_(u"Twitter Hashtags"),
        description=_(u"Comma-separated list of hashtags that should be added to a tweet."),
        required=False,
    )
