from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.portlet.static import static
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from quintagroup.portlet.static.utils import getVocabulary
from quintagroup.portlet.static import StaticStylishPortletMessageFactory as _


class IStaticStylishPortlet(static.IStaticPortlet):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    roles_excluded = schema.Tuple(
        title=_(u"Roles excluded"),
        description=_(u"Select excluded user roles."),
        value_type=schema.Choice(
            vocabulary="quintagroup.portlet.static.vocabularies.GlobalRoles"
            ),
        required=False,
        )

    roles_required = schema.Tuple(
        title=_(u"Roles required"),
        description=_(u"Select required user roles."),
        value_type=schema.Choice(
            vocabulary="quintagroup.portlet.static.vocabularies.GlobalRoles"
            ),
        required=False,
        )

    styling = schema.Choice(title=_(u"Portlet style"),
                            description=_(u"Choose a css style for the porlet. "
                                          "You can manage these entries from the plone control panel."),
                            required=False,
                            default='',
                            vocabulary='quintagroup.portlet.static.vocabularies.PortletCSSVocabulary',)


class Assignment(static.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IStaticStylishPortlet)

    styling = ''

    roles_excluded = ()

    roles_required = ()

    def __init__(self, header=u"", text=u"", omit_border=False, footer=u"",
                 more_url='', hide=False, styling='',
                 roles_excluded=(), roles_required=()):
        super(Assignment, self).__init__(header=header, text=text, omit_border=omit_border, footer=footer,
                                         more_url=more_url)

        self.styling = styling
        self.roles_excluded = roles_excluded
        self.roles_required = roles_required


class Renderer(static.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('staticstylishportlet.pt')

    @property
    def available(self):
        if self.data.roles_excluded or self.data.roles_required:
            context = aq_inner(self.context)
            mtool = getToolByName(context, 'portal_membership')

            # Determine roles
            if not mtool.isAnonymousUser():
                member = mtool.getAuthenticatedMember()
                user = member.getUser()
                roles = user.getRoles()
            else:
                roles = ()

            roles = frozenset(roles)

            # Test excluded roles
            if roles & set(self.data.roles_excluded):
                return False

            # Test required roles
            if not set(self.data.roles_required) <= roles:
                return False

        return True


class AddForm(static.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IStaticStylishPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget

    label = _(u"title_add_staticstylish_portlet", default=u"Add Static Stylish text portlet")
    description = _(u"description_staticstylish_portlet", default=u"A portlet which can display static HTML text with different styles.")

    def create(self, data):
        return Assignment(**data)


class EditForm(static.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IStaticStylishPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget

    label = _(u"title_edit_staticstylish_portlet", default=u"Edit Static Stylish text portlet")
    description = _(u"description_staticstylish_portlet", default=u"A portlet which can display static HTML text with different styles.")
