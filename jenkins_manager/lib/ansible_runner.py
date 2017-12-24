"""
this is ansible_runner wrapper
"""

import os
import subprocess
import shlex
import logging

from jenkins_manager.lib.ansibler import *

logger = logging.getLogger('runner')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '[%(asctime)s %(filename)s:%(lineno)s %(funcName)s()] %(levelname)s %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class Runner(object):
    def __init__(self, host_file='jenkins_manager/cmdber/ansible_hosts.ini', options=None, out_path='/tmp/out/'):
        logger.debug("options is " + str(options))
        self.host_file = host_file
        self.out_path = out_path
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        self.opts = {
            "connection": None,
            "module_path": None,
            "forks": 100,
            "become": True,
            "become_method": 'su',
            "become_user": 'root',
            "check": False,
            "diff": False
        }
        if options:
            self.opts.update(options)
        # Instantiate our ResultCallback for handling results as they come in
        self.results_callback = ResultCallback()
        # create inventory and pass to var manager
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources=self.host_file)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.passwords = dict(vault_pass='secret')
        self.tqm = None

    def run(self, tasks, play_name="testPlay", play_host='all', gather_facts='no'):
        """
        tasks: task list eg.[('shell','ls'),('ping','')]
             play_tasks=[
                dict(action=dict(module='shell', args='ls'), register='shell_out'),
                dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
            ]
        """
        if isinstance(tasks, tuple):
            tasks = [tasks]
        play_tasks = []
        for task in tasks:
            play_tasks.append(dict(action=dict(module=task[0], args=task[1])))

        # initialize needed objects
        Options = namedtuple('Options',
                             ['connection',
                              'module_path',
                              'forks',
                              'become',
                              'become_method',
                              'become_user',
                              'check',
                              'diff'])

        runner_options = Options(self.opts['connection'],
                                 self.opts['module_path'],
                                 self.opts['forks'],
                                 self.opts['become'],
                                 self.opts['become_method'],
                                 self.opts['become_user'],
                                 self.opts['check'],
                                 self.opts['diff'])
        logger.debug("runner_options: " + str(runner_options))

        # create play with tasks
        play_source = dict(name=play_name,
                           hosts=play_host,
                           gather_facts=gather_facts,
                           tasks=play_tasks)
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        # actually run it

        try:
            self.tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=runner_options,
                passwords=self.passwords,
                # Use our custom callback instead of the ``default`` callback plugin
                stdout_callback=self.results_callback,
            )
            self.tqm.run(play)
        finally:
            if self.tqm is not None:
                self.tqm.cleanup()

        return self.results_callback.result

    def get_hosts_info(self, refresh=False):

        if refresh:
            os.system('rm -rf ' + self.out_path + '*')
            cmd = shlex.split("ansible -u %s -i %s -m setup --tree %s all " %
                              (self.opts['become_user'], self.host_file, self.out_path))
            # cmd = shlex.split("ansible  -i %s -m setup  -tree %s all " %
            #                   (self.host_file, self.out_path))
            logger.debug("cmd is:" + "ansible -u %s -i %s -m setup --tree %s all " % (
                self.opts['become_user'], self.host_file, self.out_path))

            self.set_ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = self.set_ret.communicate()
            if err:
                raise AssertionError('generate ansible output failed:' + str(err))

        cmd = shlex.split("ansible-cmdb -t ./jenkins_manager/cmdber/tpl/json.tpl -i %s %s " %
                          (self.host_file, self.out_path))

        output, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        output = output.decode('utf8').replace("'", '"')
        # logger.debug("output is :" + output)
        if err:
            raise AssertionError('generate ansible output failed:' + str(err))
        hosts_info = self.parse_setup_data(json.loads(output))
        return hosts_info

    def gen_overview(self, endpoint=None):
        if not endpoint:
            endpoint = 'jenkins_manager/templates/base/'
            cmd = 'ansible-cmdb ' + self.out_path + ' > ' + endpoint + 'overview.html' + ' --columns name,os,ip,mem,cpus'
            print("call gent_overview function")
            ret = os.system(cmd)
            if ret != 0:
                raise AssertionError('generate gene overview filefailed:')

        return 'base/overview.html'

    @classmethod
    def parse_setup_data(cls, output):
        hosts = []
        for k, host in output.items():

            if "ansible_facts" in host:
                facts = host['ansible_facts']

                disk_total = {}
                disk_used_percentage = {}
                disk_free = {}
                for i in facts.get('ansible_mounts', []):
                    if 'size_available' in i and i['size_available'] > 1 and 'docker' not in i['mount']:
                        disk_total[i['mount']] = '{0:0.1f}'.format(i['size_total'] / 1048576000)
                        disk_free[i['mount']] = '{0:0.1f}'.format(i['size_available'] / 1048576000)
                        disk_used_percentage[i['mount']] = '{0:0.0f}'.format(
                            (i['size_total'] - i['size_available']) * 100 / i['size_total'])

                host_detail = {"Name": facts.get('ansible_hostname', '') + '.' + facts.get('ansible_domain', ''),
                               "OS": facts.get('ansible_distribution', '') + ' ' + facts.get(
                                   'ansible_distribution_version',
                                   ''),
                               "IP": facts.get('ansible_default_ipv4', {}).get('address', ''),
                               "Mac": facts.get('ansible_default_ipv4', {}).get('macaddress', ''),
                               "Arch": facts.get('ansible_architecture', 'Unk') + '/' + facts.get(
                                   'ansible_userspace_architecture', 'Unk'),
                               "Mem": '%0.1fGB' % (int(facts.get('ansible_memtotal_mb', 0)) / 1000.0),
                               "MemFree": '%0.1fGB' % (int(facts.get('ansible_memfree_mb', 0)) / 1000.0),
                               "MemUsed": '%0.1fGB' % (
                                   int(facts.get('ansible_memory_mb', {}).get('real', {}).get('used', 0)) / 1000.0),
                               "CPUs": str(facts.get('ansible_processor_count', 0)),
                               "VCPUs": str(facts.get('ansible_processor_vcpus', 0)),
                               "Virt": facts.get('ansible_virtualization_type', 'Unk') + '/' + facts.get(
                                   'ansible_virtualization_role', 'Unk'),
                               "Disk_Free": disk_free,
                               "Disk_total": disk_total,
                               "Disk_Used": disk_used_percentage,

                               }
                hosts.append(host_detail)
        return hosts


if __name__ == '__main__':
    tasks = [('shell', 'hostname')]
    opts = dict()
    opts['connection'] = 'local'
    opts['module_path'] = None
    opts['forks'] = 100
    opts['become'] = True
    opts['become_method'] = None
    opts['become_user'] = None
    runner = Runner(host_file='/Users/pengywu/GitHub/djiango-wu/jenkins_manager/cmdber/hosts.yaml', options=opts)
    ret = runner.run(tasks, play_name="test_runner", play_host='all')
    print(ret)
