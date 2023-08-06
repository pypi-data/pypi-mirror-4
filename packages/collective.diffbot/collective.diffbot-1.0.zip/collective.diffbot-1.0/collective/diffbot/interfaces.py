""" Public interfaces
"""
from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("collective")

class IDiffbotSettings(Interface):
    """ Settings for diffbot API
    """
    token = schema.TextLine(
        title=_(u"Token"),
        description=_(u"Provide token from "
                      "http://www.diffbot.com/dev/profile/"),
        required=True,
        default=u""
    )

    url = schema.TextLine(
        title=_(u"URL"),
        description=_("Diffbot API URL"),
        required=True,
        default=u"http://www.diffbot.com/api/article"
    )
