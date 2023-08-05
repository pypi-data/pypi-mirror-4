from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.views import password_change
from django.contrib import admin
from django_pci_auth.views import index, password_change_done
from django_pci_auth.forms import ValidatingPasswordChangeForm
import django.contrib.admindocs.urls


admin.autodiscover()


urlpatterns = patterns(
    '',  # prefix
    (r'^admin/doc/', include(django.contrib.admindocs.urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^change_password/$', password_change,
        {'password_change_form': ValidatingPasswordChangeForm,
        'post_change_redirect' : '/password_changed/'}),
    (r'^password_changed/$', password_change_done),
    (r'', index),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
