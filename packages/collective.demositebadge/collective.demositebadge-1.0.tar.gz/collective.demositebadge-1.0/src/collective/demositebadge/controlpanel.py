from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plone.z3cform import layout
from z3c.form import form
from collective.demositebadge.interfaces import IBadgeSettings


class ControlPanelForm(RegistryEditForm):

    form.extends(RegistryEditForm)
    schema = IBadgeSettings

ControlPanelView = layout.wrap_form(ControlPanelForm, ControlPanelFormWrapper)
ControlPanelView.label = u"Demo Site Badge"
