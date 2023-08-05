from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('ckeditor.views',
    url(r'^upload/$', 'upload', name='ckeditor_upload'),
    url(r'^browse/$', 'browse', name='ckeditor_browse'),
)
