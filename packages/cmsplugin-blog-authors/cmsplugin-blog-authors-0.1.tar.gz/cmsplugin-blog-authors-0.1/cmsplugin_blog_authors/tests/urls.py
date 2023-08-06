"""URLs for the tests of the ``cmsplugin_blog_authors`` app."""
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)
