from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('social.facebook.views',
    url(r'begin$', 'oauth_facebook_begin', name='oauth-facebook-begin'),
)

