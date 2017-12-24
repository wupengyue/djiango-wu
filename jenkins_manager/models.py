from django.db import models
from django.utils import timezone


# Create your models here.
class Node(models.Model):
    ip_address = models.CharField(max_length=50, primary_key=True)
    hostname = models.CharField(max_length=50, null=True)
    add_time = models.DateField(default=timezone.now, null=True)
    last_update_time = models.DateField(default=timezone.now, null=True)
    update_interval = models.IntegerField(default=360)

    def __str__(self):
        return self.ip_address


class Server(models.Model):
    ip = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50, null=True)
    tenant = models.CharField(max_length=50, default='Admin', null=True)
    user = models.CharField(max_length=50, default='root', null=True)
    password = models.CharField(max_length=50, default='default', null=True)
    msg = models.TextField(null=True)
    last_update_time = models.DateField(default=timezone.now, null=True)

    def __str__(self):
        return self.ip


def get_tenant(host_ip):
    srvs = Server.objects.filter(ip=host_ip)
    if srvs:
        return srvs[0].tenant
    else:
        return "Not Used"


def update_tenant(host_ip, tenant):
    srv = Server.objects.filter(ip=host_ip)
    ret = srv.update(tenant=tenant)
    # ret = srv.save()
    if ret:
        return ret
    else:
        return "Not update"


def gen_inventory(filepath='jenkins_manager/cmdber/ansible_hosts.ini'):
    inventory = ""
    srvs = Server.objects.all()
    for srv in srvs:
        inventory += srv.ip + '    ' + 'ansible_connection=ssh    ' + 'ansible_user=' + srv.user + '    ' + 'ansible_ssh_pass=' + srv.password + '\n'

    print(inventory)
    with open(filepath, 'w') as f:
        f.write('[all]\n')
        f.write(inventory)

    return True
