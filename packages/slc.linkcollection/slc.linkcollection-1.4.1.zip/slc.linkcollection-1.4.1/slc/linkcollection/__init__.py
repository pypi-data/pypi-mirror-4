from zope.i18nmessageid import MessageFactory

LinkCollectionMessageFactory = MessageFactory('slc.linkcollection')
GLOBALS = globals()


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
