Introduction
============

This product adds a browser view that generates a QRcode for the given page.
It also adds a portlet that will show a QR code. 


Use the browser view like this:

http://mysite.com/mypage/@@qrcode
To get a qrcode for http://mysite.com/mypage 

Or:
http://mysite.com/mypage/@@qrimage?view=myview
To get a qrcode for http://mysite.com/mypage/myview

Or:
http://mysite.com/@@qrimage?url=http://somewhere.com/somepage
To get a qrcode for url=http://somewhere.com/somepage


Note:
If the browser view is used on an ATlink object with external link, you will get the QR-code for that URL.