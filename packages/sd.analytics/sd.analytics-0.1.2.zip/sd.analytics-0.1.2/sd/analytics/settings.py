from persistent.dict import PersistentDict
from zope import interface
from zope import component
from zope.annotation.interfaces import IAnnotations
from plone.z3cform import z2
from plone.z3cform.widget import singlecheckboxwidget_factory
import z3c.form

from collective.dancing import channel
from collective.dancing.browser.channel import ChannelAdministrationView

from collective.dancing import browser

from interfaces import IAnalytics
from sd.analytics import MessageFactory as _

class AnalyticsForm(z3c.form.form.EditForm):

    @property
    def fields(self):
        fields = z3c.form.field.Fields(IAnalytics)
#         fields['enabled'].widgetFactory[z3c.form.interfaces.INPUT_MODE] = (
#            singlecheckboxwidget_factory)
        return fields
    
    def getContent(self):
        return dict(IAnalytics(self.context))

    @z3c.form.button.buttonAndHandler(_('Save'), name='save')
    def handle_save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = z3c.form.form.EditForm.formErrorsMessage
            return
        IAnalytics(self.context).update(data)
        self.status = z3c.form.form.EditForm.successMessage
        self.context._p_changed = True
        

class AnalyticsView(ChannelAdministrationView):

    label = _("Google Analytics setup")
    def contents(self):
        # A call to 'switch_on' is required before we can render z3c.forms.
        z2.switch_on(self)
        return AnalyticsForm(self.context, self.request)()

defaults = {'enabled':False,
            'utm_source':'newsletter',
            'utm_medium':'email',
            'utm_term':'',
            'utm_content':'',
            'utm_campaign':''}

@interface.implementer(IAnalytics)
@component.adapter(channel.IPortalNewsletters)
def analytics_settings_for_newsletters(context):
    annotations = IAnnotations(context)
    if not annotations.has_key('sd.analytics'):
        annotations['sd.analytics'] = PersistentDict(defaults)
    return annotations['sd.analytics']
