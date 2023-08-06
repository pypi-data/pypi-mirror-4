import logging
logger = logging.getLogger('rt.atmigrator')

from zope.i18nmessageid import MessageFactory
atmigratorMessageFactory = MessageFactory('rt.atmigrator')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
