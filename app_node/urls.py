from django.conf.urls import url
from app_node import views

urlpatterns = [
    # Matches any html file - to be used for node
    # Avoid using your .html in your resources.
    # Or create a separate django app_node.
    url(r'.tables_dynamic.html', views.node_table, name='node_table'),

    # The home page
    url(r'index.html', views.index, name='index'),

    # General page
    url(r'^.*\.html', views.general_html, name='general'),
    url(r'test', views.test, name='test'),
    url(r'cmdb', views.cmdb, name='cmdb'),
]