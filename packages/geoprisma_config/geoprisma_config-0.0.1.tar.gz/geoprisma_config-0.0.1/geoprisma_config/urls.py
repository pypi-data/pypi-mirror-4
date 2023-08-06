from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/', include(admin.site.urls)),
                       # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       (r'^widgets/', 'geoprisma_config.views.widgets'),
                       )

urlpatterns += patterns(
    '',
    url(r'^media-geoprisma_config/(.*)$', 'django.views.static.serve', 
        {'document_root': os.path.join(settings.PROJECT_PATH, 'geoprisma_config', 'media')},
        name='media_geoprisma_config'),
    )

#if settings.DEBUG:
urlpatterns += patterns(
    '',
    url(r'^admin-media-geoprisma_config/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(settings.PROJECT_PATH, 'geoprisma_config', 'media', 'admin')},
        name='admin_media_geoprisma_config'),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}, name="media"),
    )

#if settings.USE_I18N:
#    js_info_dict = {
#        'packages': ('geoprisma_config',),
#    }
urlpatterns += patterns(
    '',
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', None, name="jsi18n"),
    #(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    )
