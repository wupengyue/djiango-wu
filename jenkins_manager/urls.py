from django.conf.urls import url, include
from jenkins_manager import views

urlpatterns = [
    # Matches any html file - to be used for node
    # Avoid using your .html in your resources.
    # Or create a separate django app_node.
    url('login', include('django.contrib.auth.urls')),
    url(r'^servers', views.servers, name='servers'),

    # General page
    #    url(r'^.*\.html', views.general_html, name='general'),
    url(r'index', views.index, name='index'),
    url(r'test', views.test, name='test'),
    url(r'cmdb', views.cmdb, name='cmdb'),
    url(r'hosts', views.hosts, name='hosts'),
    url(r'tenants', views.tenants, name='tenants'),
    url(r'add_server', views.add_server, name='add_server'),
    url(r'del_server', views.del_server, name='del_server'),
    url(r'^login*', views.login, name='login'),
    url(r'', views.hosts, name='hosts'),

    # The home page
    url(r'', views.index, name='index'),
]
