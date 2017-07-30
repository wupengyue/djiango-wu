from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Node

import json


# Create your views here.

def index(request):
    context = {}
    template = loader.get_template('app_node/index.html')
    return HttpResponse(template.render(context, request))


def node_table(request):
    content = Node.objects.all()
    request_path = request.path.split('/')[-1]
    template_name = 'app_node/' + request_path
    return render(request, template_name, {'content': content})


def general_html(request):
    context = {}
    # The template to be loaded as per django_wu.
    # All resource paths for django_wu end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app_node/' + load_template)
    return HttpResponse(template.render(context, request))


def test(request):
    response = HttpResponse()
    msg = {'a': 'app', 'b': 'boss', 'c': 'copy'}
    response.write(json.dumps(msg))
    return response


def cmdb(request):
    response = HttpResponse()
    msg = {"ip": "192.168.1.9", "status": "SUCCESS", "changed": "false", "ping": "pong"}
    response.write(json.dumps(msg))
    return response
