from zope.interface import Interface
from zope import schema


class IBadgeSettings(Interface):
    check = schema.Bool(title=u'Display badge', default=False)
    text = schema.TextLine(title=u'Badge label', required=False,
        default=u'Demo site')
