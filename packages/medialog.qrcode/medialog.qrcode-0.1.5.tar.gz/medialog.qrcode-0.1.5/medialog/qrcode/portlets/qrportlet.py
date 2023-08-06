from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

from zope.component import getMultiAdapter

#from medialog.qrcode import MessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _



class IQRPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.
    
    anoncondition = schema.Bool(
        title=_(u"label_title_condition",
            default=u"Hide portlet for anonymous users?"),
        description=_(u"label_description_condition",
            u"Should we show the portlet only to registered users?"),
        default=True,
    )
    
    size = schema.Int(
        title=_(u"label_title_size",
            default=u"Size for the qrcode."),
        description=_(u"label_description_size",
            u"How big should the qr code image be?"),
        default = 4,
        min = 1,
        max = 40,
    )
    
    bordersize = schema.Int(
        title=_(u"label_title_bordersize",
            default=u"Size for the border."),
        description=_(u"label_description_bordersize",
            u"How big should the qr code's border be?"),
        default = 4,
        min = 4,
        max = 40
    )

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IQRPortlet)
    
    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field
    
    def __init__(self, anoncondition=True, size=4, bordersize=4):
        self.anoncondition = anoncondition
        self.size = size
        self.bordersize = bordersize

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "QR Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    
    render = ViewPageTemplateFile('qrportlet.pt')
    
    def thepath(self):
        context = self.context
        size=self.data.size
        bordersize=self.data.bordersize
        full_url = context.absolute_url() 
        qrcodepath = str(full_url) + '/qrcode?size=' + str(size) + '&border=' + str(bordersize)
        return qrcodepath
    
    @property
    def available(self):
        """Show the portlet only if condition is right."""
        
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
    	anonymous = portal_state.anonymous()  # whether or not the current user is Anonymous  
    	
    	if anonymous and self.data.anoncondition:
        	return False
        else:
			return True
			 
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IQRPortlet)

    def create(self, data):
        return Assignment(**data)        



# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IQRPortlet)
