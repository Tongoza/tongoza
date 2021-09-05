"""tongoza URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
import certbot_django.server.urls

from tongoza import settings

urlpatterns = [
    path('', include('tongozahome.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('friend/', include('friend.urls')),
    path('users/', include('users.urls')),
    path('marketing/', include('marketing.urls')),
    url(r'^\.well-known/', include(certbot_django.server.urls)),


]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        url('__debug__/', include(debug_toolbar.urls))
    ]