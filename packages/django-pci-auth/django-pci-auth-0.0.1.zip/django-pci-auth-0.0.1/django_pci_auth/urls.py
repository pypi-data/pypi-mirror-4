from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf import settings
from django.contrib.auth.views import password_change
from django.contrib.auth.views import password_change_done
from django.contrib import admin
from django_pci_auth.views import index
from django_pci_auth.forms import ValidatingPasswordChangeForm
import django.contrib.admindocs.urls


admin.autodiscover()


urlpatterns = patterns(
    '',  # prefix
    (r'^admin/doc/', include(django.contrib.admindocs.urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^change_password/$', password_change,
        {'password_change_form': ValidatingPasswordChangeForm}),
    (r'^password_changed/$', django.contrib.auth.views.password_change_done),
    (r'', index),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
