from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from tongoza import settings
from . import views

app_name = 'tongozahome'

urlpatterns = [

    # path('', views.home, name='home'),

    url(r'^$', views.HomeView.as_view(), name='home'),

    path('profile/<slug>/', views.profileDetail, name='profile'),
    path(r'post/<slug>/', views.PostDetailedView.as_view(), name='postView'),
    path(r'post-create/<pk>/', views.PostCreateView.as_view(), name='post_create'),
    path(r'post/<slug>/update', views.PostUpdateView.as_view(), name='post_update'),
    path(r'post/<slug>/delete', views.PostDeleteView.as_view(), name='post_delete'),

    # path('profile/<slug>', views.profile, name='profile'),
    path('search/', views.search_results, name='search'),


    url(r"^profile-images/(?P<slug>[\w-]+)/$", views.show_profile_images, name="profile_images", ),
    url(r'^profile-images/(?P<slug>[\w-]+)/create$', views.ProfileImageCreateView.as_view(),
        name='profile_image_create'),
    # # url(r'^product-images/(?P<slug>[\w-]+)/create$', views.product_image_create, name='product_image_create'),
    url("^profile-image/(?P<pk>[\w-]+)/update/$", views.ProfileImageUpdateView.as_view(), name="profile_image_update"),
    # url('^profile-image-(?P<pk>[\w-]+)/delete/$', views.ProfileImageDeleteView.as_view(), name="profile_image_delete"),
    url('^profile-image-(?P<pk>[\w-]+)/delete/$', views.delete_image, name="profile_image_delete"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
