from zope.i18nmessageid import MessageFactory


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

IMSTransportMessageFactory = MessageFactory('IMSTransport')
