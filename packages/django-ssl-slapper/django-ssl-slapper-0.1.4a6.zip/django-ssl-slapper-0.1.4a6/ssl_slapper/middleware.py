import re
import sha
from django.http import HttpResponseForbidden
from django.core.cache import cache
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, get_host

LOGIN_PAGE = getattr(settings, 'SSL_SLAPPER_LOGIN_PAGE', False)
if LOGIN_PAGE is False:
    try:
        LOGIN_PAGE = reverse('django.contrib.auth.views.login')
    except:
        LOGIN_PAGE = '.*/login/'

ADMIN_PAGE = getattr(settings, 'SSL_SLAPPER_ADMIN_PAGE', False)
if ADMIN_PAGE is False:
    try:
        ADMIN_PAGE = reverse('admin:index')
    except:
        ADMIN_PAGE = None

SSL_ONLY_PAGES = getattr(settings, 'SSL_SLAPPER_SSL_ONLY_PAGES', ("^%s$" % LOGIN_PAGE,"^%s$" % ADMIN_PAGE) )
SSL_REDIRECT_ANONYMOUS = getattr(settings, 'SSL_SLAPPER_SSL_REDIRECT_ANONYMOUS', True)
SSL_REDIRECT_AUTHENTICATED= getattr(settings, 'SSL_SLAPPER_SSL_REDIRECT_AUTHENTICATED', True)
SSL_REDIRECT_COOKIE= getattr(settings, 'SSL_SLAPPER_SSL_REDIRECT_COOKIE', 'logged-in' )

SSL_IGNORE_PAGES = getattr(settings, 'SSL_SLAPPER_SSL_IGNORE_PAGES', None )

SSL_ONLY_PAGES_RE= []
if SSL_ONLY_PAGES:
    for page in SSL_ONLY_PAGES:
        if page:
            SSL_ONLY_PAGES_RE.append( re.compile(page))

SSL_IGNORE_PAGES_RE= []
if SSL_IGNORE_PAGES:
    for page in SSL_IGNORE_PAGES:
        if page:
            SSL_IGNORE_PAGES_RE.append( re.compile(page))

RATE_LIMIT_MINUTES = getattr(settings, 'SSL_SLAPPER_RATE_LIMIT_MINUTES', 5)
RATE_LIMIT_KEY_FIELD = getattr(settings, 'SSL_SLAPPER_RATE_LIMIT_KEY_FIELD', 'username')
RATE_LIMIT_MAX_REQUESTS = getattr(settings, 'SSL_SLAPPER_RATE_LIMIT_MAX_REQUESTS', 10)
RATE_LIMIT_CACHE_PREFIX = getattr(settings, 'SSL_SLAPPER_RATE_LIMIT_CACHE_PREFIX','rl-')
RATE_LIMIT_PAGES = getattr(settings, 'SSL_SLAPPER_RATE_LIMIT_PAGES', SSL_ONLY_PAGES)
RATE_LIMIT_PAGES_RE= []

if RATE_LIMIT_PAGES:
    for page in RATE_LIMIT_PAGES:
        if page:
            RATE_LIMIT_PAGES_RE.append( re.compile(page))
    
def is_dev_server(request):        
    server = request.META.get('wsgi.file_wrapper', None)
    if server is not None and server.__module__ == 'wsgiref.util':
        return True
    return False

class ssl_redirect:
    def is_ssl_only(self,path):
        for ssl_only_page_re in SSL_ONLY_PAGES_RE:
            if ssl_only_page_re.match(path):
                return True
        return False

    def is_ignored(self,path):
        for page_re in SSL_IGNORE_PAGES_RE:
            if page_re.match(path): 
                return True
        return False

    def process_response(self, request, response):
        if hasattr(request,'user'):
            if not request.user.is_authenticated():
                #we are not logged in?  Delete cookie!
                response.delete_cookie(SSL_REDIRECT_COOKIE)
                
            if SSL_REDIRECT_AUTHENTICATED and request.user.is_authenticated():
                max_age = 365 * 24 * 60 * 60  #one year
                response.set_cookie( SSL_REDIRECT_COOKIE, 'true',max_age )
        return response
        
    def process_request(self, request):
        """redirect if SSL to settigns.SSL or NO_SSL to http """
        
        assert hasattr(request,'user'), \
            "request.user not found.  Please add     'ssl_slapper.middleware.ssl_redirect' and   'ssl_slapper.middleware.rate_limit', after     'django.contrib.auth.middleware.AuthenticationMiddleware', in your setting"
        
        if request.is_secure():
            if SSL_REDIRECT_ANONYMOUS:
                if not request.user.is_authenticated() and not self.is_ssl_only(request.path) and not self.is_ignored(request.path):
                    return self._redirect(request, False)
                
        else:
            if self.is_ssl_only(request.path):
                return self._redirect(request, True)
            
            if SSL_REDIRECT_AUTHENTICATED and request.COOKIES.has_key( 'logged-in' )and not self.is_ignored(request.path):
                return self._redirect(request, True)

        return None

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol,get_host(request),request.get_full_path())
        if is_dev_server(request):
            print 'ignoring redirect to %s on devbox' % newurl
            return None

        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponseRedirect(newurl)
    
class rate_limit:
    def is_rate_limited(self,path):
        for rate_limit_page_re in RATE_LIMIT_PAGES_RE:
            if rate_limit_page_re.match(path): 
                return True
        return False

    def process_request(self, request):
        if self.is_rate_limited(request.path):
            counts = self.get_counters(request).values()
            self.cache_incr(self.current_key(request))
            
            if sum(counts) >= RATE_LIMIT_MAX_REQUESTS:
                return HttpResponseForbidden('Too many login attempts.  Your account has been locked.  Please try again later.')

        return None

    def cache_get_many(self, keys):
        return cache.get_many(keys)
    
    def cache_incr(self, key):
        # memcache is only backend that can increment atomically
        try:
            cache.incr(key)
        except (AttributeError,ValueError):
            cache.set(key, cache.get(key, 0) + 1, self.expire_after())
    
    def should_ratelimit(self, request):
        return True
    
    def get_counters(self, request):
        return self.cache_get_many(self.keys_to_check(request))
    
    def keys_to_check(self, request):
        extra = self.key_extra(request)
        now = datetime.now()
        return [
            '%s%s-%s' % (
                RATE_LIMIT_CACHE_PREFIX,
                extra,
                (now - timedelta(minutes = minute)).strftime('%Y%m%d%H%M')
            ) for minute in range(RATE_LIMIT_MINUTES + 1)
        ]
    
    def current_key(self, request):
        return '%s%s-%s' % (
            RATE_LIMIT_CACHE_PREFIX,
            self.key_extra(request),
            datetime.now().strftime('%Y%m%d%H%M')
        )
    
    def key_extra(self, request):
        # By default, their IP address is used

        if RATE_LIMIT_KEY_FIELD and request.REQUEST.get(RATE_LIMIT_KEY_FIELD):
            return  sha.new(request.REQUEST.get(RATE_LIMIT_KEY_FIELD, '')).hexdigest()
        else:
            return request.META.get('REMOTE_ADDR', '')

    
    def disallowed(self, request, fn, *args, **kwargs):
        "Over-ride this method if you want to log incidents"
        return HttpResponseForbidden('Rate limit exceeded')
    
    def expire_after(self):
        "Used for setting the memcached cache expiry"
        return (RATE_LIMIT_MINUTES + 1) * 60


