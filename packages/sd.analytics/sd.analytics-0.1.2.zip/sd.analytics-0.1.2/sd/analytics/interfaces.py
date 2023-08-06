from zope import interface
from zope import schema

from sd.analytics import MessageFactory as _

class IAnalytics(interface.Interface):
    # titles and descriptions lifted from google own "URL builder"
    # http://www.google.com/support/analytics/bin/answer.py?hl=en&answer=55578

    enabled = schema.Bool(
        title=_(u"Enable google analytics for newsletters"),
        description=_(u"URL's in outgoing newsletters will be rewritten to enable tracking with google analytic. See http://www.google.com/analytics/index.html for info."))

    utm_source = schema.TextLine(
        title=_(u"Campaign Source (utm_source)"),
        description=_(u"Use utm_source to identify a search engine, newsletter name, or other source. Example: utm_source=google."),
        required=True)

    utm_medium = schema.TextLine(
        title=_(u"Campaign Medium (utm_medium)"),
        description=_(u"Use utm_medium to identify a medium such as email or cost-per- click. Example: utm_medium=cpc."),
        required=True)

    utm_term = schema.TextLine(
        title=_(u"Campaign Term (utm_term)"),
        description=_(u"Used for paid search. Use utm_term to note the keywords for this ad. Example: utm_term=running+shoes."),
        required=False)

    utm_content = schema.TextLine(
        title=_(u"Campaign Content (utm_content)"),
        description=_(u"Used for A/B testing and content-targeted ads. Use utm_content to differentiate ads or links that point to the same URL. Examples: utm_content=logolink or utm_content=textlink."),
        required=False)

    utm_campaign = schema.TextLine(
        title=_(u"Campaign Name (utm_campaign)"),
        description=_(u"Keep blank to use channel id (and be able to differentiate between different newsletters). Used for keyword analysis. Use utm_campaign to identify a specific product promotion or strategic campaign. Example: utm_campaign=spring_sale."),
        required=False)

