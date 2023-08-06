""" Control Panel
"""
from zope.component import queryUtility
from zope.interface import implements
from collective.diffbot.interfaces import _
from collective.diffbot.interfaces import IDiffbotSettings
from plone.app.controlpanel.form import ControlPanelForm
from plone.registry.interfaces import IRegistry
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from zope.formlib import form

class DiffbotControlPanel(ControlPanelForm):
    """ Diffbot API
    """
    form_fields = form.FormFields(IDiffbotSettings)
    label = _(u"Diffbot API")
    description = _(u"Diffbot API settings")
    form_name = _(u"Diffbot settings")

class DiffbotControlPanelAdapter(SchemaAdapterBase):
    """ Form adapter
    """
    implements(IDiffbotSettings)

    def __init__(self, context):
        super(DiffbotControlPanelAdapter, self).__init__(context)
        self._settings = None

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            self._settings = queryUtility(
                IRegistry).forInterface(IDiffbotSettings, False)
        return self._settings


    @property
    def token(self):
        """ Token getter
        """
        return self.settings.token

    @token.setter
    def token(self, value):
        """ Token setter
        """
        self.settings.token = value

    @property
    def url(self):
        """ URL getter
        """
        return self.settings.url

    @url.setter
    def url(self, value):
        """ URL setter
        """
        self.settings.url = value
