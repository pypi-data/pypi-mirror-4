"""URLs for the ``cmsplugin_blog_attachments`` project."""
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)
