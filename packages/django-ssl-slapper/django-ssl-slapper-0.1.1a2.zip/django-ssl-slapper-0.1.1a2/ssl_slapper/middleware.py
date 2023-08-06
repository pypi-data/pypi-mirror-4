import re
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, get_host
SSL_ONLY_PAGES = getattr(settings, 'SSL_SLAPPER_SSL_ONLY_PAGES', ('.*/login/',))
SSL_REDIRECT_ANONYMOUS = getattr(settings, 'SSL_SLAPPER_SSL_REDIRECT_ANONYMOUS', True)
SSL_REDIRECT_AUTHENTICATED= getattr(settings, 'SSL_SLAPPER_SSL_REDIRECT_AUTHENTICATED', True)

SSL_ONLY_PAGES_RE= []
for ssl_only_page in SSL_ONLY_PAGES:
    SSL_ONLY_PAGES_RE.append( re.compile(ssl_only_page))

def page_is_ssl_only(path):
    for ssl_only_page_re in SSL_ONLY_PAGES_RE:
        if ssl_only_page_re.match(path): 
            return True
    return False
        
class ssl_slapper:
    def process_response(self, request, response):
        if hasattr(request,'user'):
            if not request.user.is_authenticated():
                #we are not logged in?  Delete cookie!
                response.delete_cookie('logged-in')
                
            if SSL_REDIRECT_AUTHENTICATED and request.user.is_authenticated():
                max_age = 365 * 24 * 60 * 60  #one year
                response.set_cookie( 'logged-in', 'true',max_age )
        return response
        
    def process_request(self, request):
        """redirect if SSL to settigns.SSL or NO_SSL to http """

        server = request.META.get('wsgi.file_wrapper', None)
        if server is not None and server.__module__ == 'wsgiref.util':
            print 'ignoring ssl on devbox'
            return None

        if request.is_secure():
            if SSL_REDIRECT_ANONYMOUS:
                if not request.user.is_authenticated() and not page_is_ssl_only(request.path):
                    return self._redirect(request, False)
                
        else:
            if page_is_ssl_only(request.path):
                return self._redirect(request, True)
            
            if SSL_REDIRECT_AUTHENTICATED and request.COOKIES.has_key( 'logged-in' ):
                return self._redirect(request, True)

        return None

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol,get_host(request),request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponseRedirect(newurl)