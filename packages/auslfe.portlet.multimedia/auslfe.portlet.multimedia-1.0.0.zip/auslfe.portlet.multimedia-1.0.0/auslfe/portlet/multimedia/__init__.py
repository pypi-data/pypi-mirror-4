from zope.i18nmessageid import MessageFactory
AuslfePortletMultimediaMessageFactory = MessageFactory('auslfe.portlet.multimedia')
import logging
logger = logging.getLogger("auslfe.portlet.multimedia")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
