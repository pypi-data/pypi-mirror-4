Django SSL Slapper
===================

Django SSL Redirect is a middleware that ensures secured URLs and only secured URLs are accessed securely over HTTPS.

Installation
------------

Copy into project.  

Add     ```ssl_slapper.middleware.ssl_slapper'``` to middleware in your django settings file


Securing Views
--------------

To secure a url simply add it to the list in your settings file.  For example:
```SSL_ONLY_PAGES = ('/account/login/','/admin/.*')```



Settings
--------
```SSL_ONLY_PAGES = ('/account/login/','/admin/.*')```
'''SSL_REDIRECT_ANONYMOUS''': Set to true to redirect anonymous users to http.