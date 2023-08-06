from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName

from quintagroup.portlet.static.utils import getVocabulary
from quintagroup.portlet.static import StaticStylishPortletMessageFactory as _


# fallback in case there is no portlet_dropdown lines property inside
# staticporlet_properties property sheed in portal_properties tool
PORTLET_CSS_STYLES = (
    (u"portletStaticClassOne", u"Class One"),
)

class PortletCSSVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        styles = getVocabulary(context)
        if styles is None:
            styles = PORTLET_CSS_STYLES
        charset = self._charset(context)
        items = []
        for value, title in styles:
            if not isinstance(title, unicode):
                title = title.decode(charset)
            if not isinstance(value, unicode):
                value = value.decode(charset)
            items.append(SimpleTerm(value, value, _(title)))
        return SimpleVocabulary(items)

    def _charset(self, context):
        pp = getToolByName(context, 'portal_properties', None)
        if pp is not None:
            site_properties = getattr(pp, 'site_properties', None)
            if site_properties is not None:
                return site_properties.getProperty('default_charset', 'utf-8')
        return 'utf-8'

PortletCSSVocabulary = PortletCSSVocabulary()


class GlobalRolesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        roles = context.getGlobalPortalRoles()

        return SimpleVocabulary(
            [SimpleTerm(
                role, role,
                translate(role, domain="plone", context=context.REQUEST) \
                ) for role in roles]
            )


GlobalRolesVocabulary = GlobalRolesVocabulary()
