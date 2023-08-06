from plone.app.registry.browser import controlpanel

from collective.gsa import GSAMessageFactory as _
from collective.gsa.interfaces import IGSASchema


class GSASettingsEditForm(controlpanel.RegistryEditForm):
    
    schema = IGSASchema

    label = _('GSA settings')
    description = _('Settings to enable and configure GSA integration for Plone.')
 

class GSASettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = GSASettingsEditForm

