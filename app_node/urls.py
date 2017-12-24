from django.conf.urls import url
from app_node import views

urlpatterns = [
    # Matches any html file - to be used for node
    # Avoid using your .html in your resources.
    # Or create a separate django app_node.
    url(r'^servers', views.servers, name='servers'),

    # General page
    url(r'^.*\.html', views.general_html, name='general'),
    url(r'test', views.test, name='test'),
    url(r'cmdb', views.cmdb, name='cmdb'),

    # The home page
    url(r'', views.index, name='index'),
]
