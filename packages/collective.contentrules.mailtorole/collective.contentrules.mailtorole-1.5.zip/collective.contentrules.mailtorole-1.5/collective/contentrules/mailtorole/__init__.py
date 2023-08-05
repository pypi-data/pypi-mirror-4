from zope.i18nmessageid import MessageFactory

mailtoroleMessageFactory = MessageFactory(
    'collective.contentrules.mailtorole')


def initialize(context):
    """Intializer called when used as a Zope 2 product."""
