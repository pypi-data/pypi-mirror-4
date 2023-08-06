from collective.dancing.browser import controlpanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ControlPanelView(controlpanel.ControlPanelView):
    contents = ViewPageTemplateFile('controlpanel-links.pt')



