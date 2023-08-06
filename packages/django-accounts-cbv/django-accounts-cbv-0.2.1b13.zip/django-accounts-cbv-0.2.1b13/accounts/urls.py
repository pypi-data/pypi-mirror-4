from . import views
from django.conf.urls import patterns, url


urlpatterns = patterns('accounts.views',
    url(r'^login/$', views.Login.as_view(), name='auth_login'),
    url(r'^logout/$', views.Logout.as_view(), name='auth_logout'),
    url(r'^password/reset/$', views.PasswordReset.as_view(), name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.PasswordResetConfirm.as_view(), name='auth_password_reset_confirm'),
    url(r'^profile/$', views.UserUpdate.as_view(), name='accounts_profile'),
)
