import qrcode

from cStringIO import StringIO
from PIL import Image
#from PIL import ImageOps
from PIL.PngImagePlugin import PngImageFile

from zope.interface import implements, Interface
from Products.Five import BrowserView

from zope import schema
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic

# zope.18n message translator for your add-on product
#from medialog.qrcode import MessageFactory as _



class IQRImage(Interface):
    """ QR Image view interface """
    
    def test():
        """ test method"""

class QRImage(BrowserView):
    """ A browser view to create QR codes """
    
    def __call__(self, REQUEST):
    	size = self.request.get('size', 10)  #For later use
    	border = self.request.get('border', 4)  #For later use
    	view = self.request.get('view', '')  #Makes it possible to add another view to the url
    	other_url = self.request.get('url', '')    #Makes it possible to use another url
    	context = self.context
    	url = context.absolute_url()
    	if context.getLayout() == 'link_redirect_view':
    	    if context.getRemoteUrl().startswith('.'):
                # we just need to adapt ../relative/links, /absolute/ones work anyway
                # -> this requires relative links to start with ./ or ../
                context_state = context.restrictedTraverse('@@plone_context_state')
                url = context_state.canonical_object_url() + '/' + context.getRemoteUrl()
            else:
                url = context.getRemoteUrl()
    	
    	if view <> '':
    		url = url + '/' + view
    	if other_url <> '':
    		url = other_url		
    		
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=border,
            )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image()
    		
    	#img = qrcode.make(url)
    	output = StringIO()
    	img.save(output)
    	self.request.response.setHeader('Content-Type', 'image/png')
    	return output.getvalue()
    	
    	
    	


class IQrSummaryView(Interface):
    """ Allowed template variables exposed from the view.
    """

    # Item list as iterable Products.CMFPlone.PloneBatch.Batch object
    contents = schema.Object(Interface)


class QrSummaryView(BrowserView):
    """
    List summary information with qr codes.

    Batch results.
    """
    implements(IQrSummaryView)

    def query(self, start, limit, contentFilter):
        """ Make catalog query for the folder listing.

        @param start: First index to query

        @param limit: maximum number of items in the batch

        @param contentFilter: portal_catalog filtering dictionary with index -> value pairs.

        @return: Products.CMFPlone.PloneBatch.Batch object
        """

        # Batch size
        b_size = limit

        # Batch start index, zero based
        b_start = start

        # We use different query method, depending on
        # whether we do listing for topic or folder
        if IATTopic.providedBy(self.context):
            # ATTopic like content
            # Call Products.ATContentTypes.content.topic.ATTopic.queryCatalog() method
            # This method handles b_start internally and
            # grabs it from HTTPRequest object
            return self.context.queryCatalog(contentFilter, batch=True, b_size=b_size)
        else:
            # Folder or Large Folder like content
            # Call CMFPlone(/skins/plone_scripts/getFolderContents Python script
            # This method handles b_start parametr internally and grabs it from the request object
            return self.context.getFolderContents(contentFilter, batch=True, b_size=b_size)

    def __call__(self):
        """ Render the content item listing.
        """

        # How many items is one one page
        limit = 3

        # What kind of query we perform?
        # Here we dont limit results
        filter = { "portal_type" : "ATDocument" }

        # Read the first index of the selected batch parameter as HTTP GET request query parameter
        start = self.request.get("b_start", 0)

        # Perform portal_catalog query
        self.contents = self.query(start, limit, filter)

        # Return the rendered template (qrsummaryview.pt), with content listing information filled in
        return self.index()
        