from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from demo import views

urlpatterns = patterns('',
    url(r'^$', views.Home.as_view(), name='home'),

    url(r'^account/register/$', 'demo.views.register', name='register'),
    url(r'^account/profile/$', 'demo.views.profile', name='profile'),
    url(r'^account/unverify/(?P<id>\d+)/$',
        'demo.views.remove_computer_verification', name='unverify'),

    url(r'^account/logout/$', 'django.contrib.auth.views.logout',
        name='logout'),

    url(r'^tf/', include('two_factor.urls', 'tf')),

    # Examples:
    # url(r'^demo/', include('demo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
