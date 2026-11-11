from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('', include('accounts.urls')),
    path('', include('projects.urls')),
    path('', include('ia.urls')),
]

if settings.DEBUG_TOOLBAR_ENABLED:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
