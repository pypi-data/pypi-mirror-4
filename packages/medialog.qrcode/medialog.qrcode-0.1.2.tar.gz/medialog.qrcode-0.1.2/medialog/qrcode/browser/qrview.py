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
    	box_size = self.request.get('size', 10)  #For later use
    	border = self.request.get('border', 10)  #For later use
    	view = self.request.get('view', '')  #Makes it possible to add another view to the url
    	url = self.context.absolute_url()
    	if view <> '':
    		url = url + '/' + view
    	img = qrcode.make(url)
    	output = StringIO()
    	img.save(output)
    	self.request.response.setHeader('Content-Type', 'image/png')
    	return output.getvalue()