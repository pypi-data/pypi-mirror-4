from zope.i18nmessageid import MessageFactory

_ = MessageFactory("collective.dms.basecontent")

from ._field import LocalRolesToPrincipals


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
