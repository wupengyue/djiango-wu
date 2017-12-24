from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Node

import json
import requests


# Create your views here.

def index(request):
    context = {}
    template = loader.get_template('app_node/index.html')
    return HttpResponse(template.render(context, request))


def servers(request):
    contents = []
    # path = 'http://10.74.27.239:8080/computer/api/json'
    path = 'http://127.0.0.1:8080/computer/api/json'
    r = requests.get(path)
    computers = r.json()['computer']

    # content = Node.objects.all()
    # request_path = request.path.split('/')[-1]
    # template_name = 'app_node/' + request_path
    for computer in computers:
        computer['hostname'] = computer['displayName']
        computer['ip_address'] = computer['displayName'].split("-")[0]
        computer['response_time'] = computer['monitorData']['hudson.node_monitors.ResponseTimeMonitor']['average']
        contents.append(computer)

    return render(request, "app_node/servers.html", {'contents': contents})


def general_html(request):
    context = {}
    # The template to be loaded as per my_sites.
    # All resource paths for my_sites end in .html.

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
