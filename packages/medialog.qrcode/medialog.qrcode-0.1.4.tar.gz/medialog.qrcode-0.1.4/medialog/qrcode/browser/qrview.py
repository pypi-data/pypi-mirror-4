import qrcode

from cStringIO import StringIO
from PIL import Image
#from PIL import ImageOps
from PIL.PngImagePlugin import PngImageFile

from zope.interface import implements, Interface
from Products.Five import BrowserView

class IQRImage(Interface):
    """ QR Image view interface """
    
    def test():
        """ test method"""

class QRImage(BrowserView):
    """ A browser view to create QR codes """
    
    def __call__(self, REQUEST):
    	size = self.request.get('size', 40)  #For later use
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