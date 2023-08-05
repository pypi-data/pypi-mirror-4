from urllib2 import urlopen
from zope import interface
from zope import schema
from zope import i18nmessageid

from plone.app.registry.browser import controlpanel as base
from plone.registry import field
from z3c.form.interfaces import WidgetActionExecutionError
_ = i18nmessageid.MessageFactory('collective.domainvalidator')


class ISettingsSchema(interface.Interface):
    """Settings for this addon"""

    activated = schema.Bool(title=_(u"Is activated"),
                            description=_(u"Uncheck to unactivate this addon"),
                            default=True)

    mapping = schema.List(title=_(u"URL - Language mapping"),
                          default=[],
                          value_type=field.URI(title=_(u"URL|LANG"),
                                       description=_(u"http://mysite.com|en")))


class ControlPanelForm(base.RegistryEditForm):
    schema = ISettingsSchema
    label = _(u"Domain validator control panel")

    def extractData(self):
        data, errors = super(ControlPanelForm, self).extractData()
        if errors:
            return data, errors

        data, errors = self.validate_mapping(data, errors)
        return data, errors

    def raise_error_message(self, message, field=None):
        error_instance = interface.Invalid(message)
        raise WidgetActionExecutionError(field, error_instance)

    def validate_mapping(self, data, errors=None):
        mapping_field = 'mapping'
        if errors is None:
            errors = ()

        for mapping in data.get('mapping', None):

            if len(mapping.split('|')) != 2:
                msg = _(u"must be of url|lang of a ISiteRoot")
                self.raise_error_message(msg, field=mapping_field)
                return data, errors

            url = mapping.split('|')[0]
            try:
                url_opened = urlopen(url, timeout=2)
            except IOError:
                msg = _(u"an url provided do not exists")
                self.raise_error_message(msg, field=mapping_field)
                return data, errors

            if url_opened.code != 200:
                msg = _(u"url do not return status 200")
                self.raise_error_message(msg, field=mapping_field)

        return data, errors


class ControlPanelView(base.ControlPanelFormWrapper):
    form = ControlPanelForm
