from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class DemoSiteBadgeView(BrowserView):

    def get_demo_label(self):
        registry = getUtility(IRegistry)
        label = registry[
            'collective.demositebadge.interfaces.IBadgeSettings.text']

        if registry[
            'collective.demositebadge.interfaces.IBadgeSettings.check'] and \
           label:
            return label
        else:
            return ''
