from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse_lazy

from account.views import home_view, login_view


urlpatterns = patterns('',
    url(r'^logout/$', logout, kwargs={'next_page': reverse_lazy('account-login')}, name="account-logout"),
    url(r'^login/$', login_view, name="account-login"),
    url(r'^$', home_view, name="home"),
    url(r'', include('social_auth.urls')),
)
