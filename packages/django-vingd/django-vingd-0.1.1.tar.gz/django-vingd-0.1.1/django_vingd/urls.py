from django.conf.urls import patterns, url
from .views import OrderView, VerifyView

urlpatterns = patterns('',
    url(r'^order/(?P<nametag>\w+)/$', OrderView.as_view(), name='vingd_order'),
    url(r'^verify/$', VerifyView.as_view(), name='vingd_verify'),
)
