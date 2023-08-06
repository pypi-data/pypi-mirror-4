import os

from Products.Five.browser import BrowserView


class CSSHoverView(BrowserView):
    """Return csshover.htc js for IE < 7, this requires python class only
    because of need to set custom content type for that resource.
    """

    def __call__(self):
        """Main method"""
        resource = file(os.path.join(os.path.dirname(__file__),
                                     'resources', 'csshover.htc'), 'r').read()
        response = self.request.response
        response.setHeader('Content-Type', 'text/x-component')

        # cache in browser for 1 year and in proxy for 2 month
        response.setHeader('Cache-Control',
                           'max-age=31536000, s-maxage=5184000, public')

        # enabling gzip compression
        response.enableHTTPCompression(REQUEST=self.request)
        return resource
