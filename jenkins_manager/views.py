import json
import time
import requests
import logging
import pdb

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import loader
from django.contrib import auth
from jenkins_manager.lib.ansible_runner import Runner
from jenkins_manager.lib.parseconfig import yaml_loader
from .models import Server, get_tenant, update_tenant, gen_inventory
from django.contrib.auth.decorators import login_required
from .forms import UserForm

log = logging.getLogger(__name__)
config = yaml_loader('jenkins_manager/config.yml')
runner = Runner()


# Create your views here.
def index(request):
    context = {}
    template = loader.get_template('base/index.html')
    return HttpResponse(template.render(context, request))


def logout(request):
    return HttpResponse('Welcome,  <a href="/logout/" trarget="_blank"> logout</a>')


def login(request):
    return render_to_response('base/login.html')
    # return HttpResponse(template.render(context, request))


def login(request):
    form = UserForm(request.POST)
    log.debug("request.method is :" + request.method)

    if request.method == 'POST':
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            log.debug("username is :" + username)
            log.debug("password is :" + password)
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return render(request, 'base/servers.html')
            else:
                form.add_error('password', 'username and password not match!')
    return render(request, 'base/login.html', {'form': form})


# @login_required
def servers(request):
    contents = []
    path = 'http://10.74.27.239:8080/computer/api/json'
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

    return render(request, "base/servers.html", {'contents': contents})


# @login_required
def add_server(request):
    new_server = Server.objects.create(name="ops.ipcdn.cisco.com", ip="10.74.26.114")
    return HttpResponse(new_server.name)


# @login_required
def del_server(request):
    server = Server.objects.filter(name="ops.ipcdn.cisco.com")
    del_server = server.delete()
    return HttpResponse(del_server)


# @login_required
def tenants(request):
    ip = ""
    tenant = ""
    if request.method == 'POST':
        if 'ip' in request.POST:
            ip = request.POST['ip']
        if 'tenant' in request.POST:
            tenant = request.POST['tenant']
        update_tenant(ip, tenant)

    if request.method == 'GET':
        ip = ""
        tenant = ""
    message = {'ip': ip, 'tenant': tenant}
    log.debug("message is :" + str(message))
    # return HttpResponse(message)
    return JsonResponse(message)


# @login_required
def hosts(request):
    # show server manager by ansible db

    refresh = False
    host_file = 'jenkins_manager/cmdber/ansible_hosts.ini'
    if refresh:
        gen_inventory(host_file)
    runner = Runner(host_file)
    hosts = runner.get_hosts_info(refresh)
    for host in hosts:
        host['tenant'] = get_tenant(host['IP'])

    # contents = []  # path = 'http://10.74.27.239:8080/computer/api/json'
    # r = requests.get(path)
    # computers = r.json()['computer']

    # content = Node.objects.all()
    # request_path = request.path.split('/')[-1]
    # template_name = 'app_node/' + request_path
    # for computer in computers:
    #     computer['hostname'] = computer['displayName']
    #     computer['ip_address'] = computer['displayName'].split("-")[0]
    #     computer['response_time'] = computer['monitorData']['hudson.node_monitors.ResponseTimeMonitor']['average']
    #     contents.append(computer)
    #
    # return render(request, "base/servers.html", {'contents': contents})
    # response.write(json.dumps(hosts, indent=4))
    return render(request, "base/hosts.html", {'contents': hosts})


# @login_required
def general_html(request):
    context = {}
    # The template to be loaded as per my_sites.
    # All resource paths for my_sites end in .html.
    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('base/' + load_template)
    return HttpResponse(template.render(context, request))


def test(request):
    response = HttpResponse()
    msg = {'a': 'app', 'b': 'boss', 'c': 'copy'}
    response.write(json.dumps(msg))
    return JsonResponse(msg)


# @login_required
def cmdb(request):
    overview = runner.gen_overview()

    return render_to_response("base/cmdb.html")
