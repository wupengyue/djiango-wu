"""gentella URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # url(r'^app_temple', include('app_temple.urls')),

    # # app_node/ -> Genetelella UI and resources
    # url(r'^app_node', include('app_node.urls')),
    # include  auth app's urls module
    url(r'^users/', include('django.contrib.auth.urls')),
    # default url to jenkins_manager
    url(r'', include('jenkins_manager.urls'))

]
