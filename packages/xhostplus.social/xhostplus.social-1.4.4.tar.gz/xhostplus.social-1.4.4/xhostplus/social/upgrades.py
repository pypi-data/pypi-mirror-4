import logging

from transaction import commit
from zope.component import getUtility
from Products.CMFPlone.utils import getToolByName

from xhostplus.social.interfaces.configuration import ISocialConfiguration

def add_button_toggle_configuration(obj):
    obj.enable_facebook = True
    obj.enable_gplus = True
    obj.enable_twitter = True
    obj.enable_linkedin = False

def add_hashtag_configuration(obj):
    obj.twitter_hashtags = u""


def upgrade_12_to_14(context, logger=None):
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('xhostplus.social')

    try:
        portal = getToolByName(context, "portal_url").getPortalObject()
        settings = getUtility(ISocialConfiguration)
    except:
        logger.info("No migration needed because no settings were found.")
        return

    add_button_toggle_configuration(settings)
    logger.info("Migrated button configuration.")

    add_hashtag_configuration(settings)
    logger.info("Migrated hashtag configuration.")

    commit()
    portal._p_jar.sync()
