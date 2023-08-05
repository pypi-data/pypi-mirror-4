from zope.i18nmessageid import MessageFactory

GSAMessageFactory = MessageFactory('collective.gsa')


from AccessControl import allow_module
allow_module('collective.gsa.utils')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
