from django.conf.urls import patterns, include, url
from mainapp.views import volume
from mainapp.views import client
from mainapp.views import grand_total

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xsanio_server.views.home', name='home'),
    # url(r'^xsanio_server/', include('xsanio_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(
        r'^$',
        grand_total.display_grand_total.as_view(),
        name='home_view'
    ),
    url(
        r'^volumes/$',
        volume.display_volume_list.as_view(),
        name='volume_list_view'
    ),
    url(
        r'^volumes/(?P<pk>\d+)/$',
        volume.display_volume_detail.as_view(),
        name='volume_detail_view'
    ),
    url(
        r'^volumes/(?P<pk>\d+)/order_by/(?P<stat_type_order>.+)/$',
        volume.display_volume_detail.as_view(),
        name='volume_detail_view_sorted'
    ),
    url(
        r'^clients/$',
        client.display_client_list.as_view(),
        name='client_list_view'
    ),
    url(
        r'clients/(?P<pk>\d+)/$',
        client.display_client_detail.as_view(),
        name='client_detail_view'
    ),
    url(
        r'clients/(?P<pk>\d+)/order_by/(?P<stat_type_order>.+)/$',
        client.display_client_detail.as_view(),
        name='client_detail_view_sorted'
    )
)