#!/usr/bin/env bash
wspath=`pwd`

cd /root/upgrade
. ./get_ip.sh
. ./docker_cmd.sh
. ./install_rpm.sh

echo "current director wspath is: ${wspath}"
docker_compose_ip='10.140.105.113'
repo_ip='10.140.105.143'
/bin/cp -f /etc/resolv.conf /etc/resolv.conf.bkup
/bin/cp -f /etc/hosts  /etc/hosts.bkup
setenforce 0


old_omd_core_rpm="omd-core-3.5.3-b21.x86_64.rpm"
old_omd_salt_rpm="omd-os-salt-3.5.1-b8.x86_64.rpm"
OMD_PKG_URL='http://10.74.27.239:8080/view/OMD_3.6.1_release/job/OMD_3.6.1_openmd_build/lastSuccessfulBuild/artifact/salt/.build/omd-core-3.6.1-b20.tgz'
OMD_PKG_tgz=`echo ${OMD_PKG_URL} |awk -F '/'  '{print $NF}'`
new_omd_core_rpm=`echo ${OMD_PKG_tgz} |awk -F '.tgz'  '{print $1}'`.x86_64.rpm
echo "new_omd_core_rpm is: $new_omd_core_rpm"

if [[ ! -f "/root/AC9/${OMD_PKG_tgz}" ]]; then
    echo "/root/AC9/${OMD_PKG_tgz} don't exist, downloading ..."
    wget -q ${OMD_PKG_URL} -O /root/AC9/${OMD_PKG_tgz}
fi

if [[ ! -f "/root/AC9/${new_omd_core_rpm}" ]]; then
    rm -f /root/AC9/omd_core_packages/*
    tar xf /root/AC9/${OMD_PKG_tgz} -C /root/AC9/
    if [[ $? -ne 0 ]]; then
        echo "tar xf /root/AC9/${OMD_PKG_tgz} failed"
        exit 1
    fi
fi

echo "update repo"
scp /root/AC9/omd_core_packages/*rpm root@${repo_ip}:/opt/http/repo/extra_rpms_73
ssh root@${repo_ip}<<'ENDSSH'
    createrepo --update  /opt/http/repo/extra_rpms_73
    systemctl status httpd
ENDSSH


OMD_SALT_URL='http://engci-maven-master.cisco.com/artifactory/open-cdn-release/omd-os-salt-3.6.1-b8.tgz'
OMD_SALT_tgz=`echo ${OMD_SALT_URL} |awk -F '/'  '{print $NF}'`
new_omd_salt_rpm=`echo ${OMD_SALT_tgz} |awk -F '.tgz'  '{print $1}'`.x86_64.rpm
echo "new_omd_salt_rpm is: $new_omd_salt_rpm"

if [[ ! -f "/root/AC9/${OMD_SALT_tgz}" ]]; then
    echo "/root/AC9/${OMD_SALT_tgz} don't exist, downloading ..."
    wget  ${OMD_SALT_URL}
    mv ${OMD_SALT_tgz} /root/AC9/
fi

if [[ ! -f "/root/AC9/${new_omd_salt_rpm}" ]]; then
    tar xf /root/AC9/${OMD_SALT_tgz} -C /root/AC9/
    if [[ $? -ne 0 ]]; then
        echo "tar xf /root/AC9/${OMD_SALT_tgz} failed"
        exit 1
    fi
fi

echo "update repo"





source /root/venv/bin/activate
cd /root/OMD/automation
git checkout .
mkdir -p reports || /bin/true
export PYTHONPATH=`pwd`
TESTBED_ID="upgrade"



echo "==========================step 1 prepare AC8 testbed=========================="
cp -f /root/AC8/${old_omd_core_rpm} /tmp/
cp -f /root/AC8/${old_omd_salt_rpm} /tmp/
install_rpm ${old_omd_salt_rpm}
install_rpm ${old_omd_core_rpm}
cat ~/.ssh/id_rsa.pub > /srv/salt/users/authorized_keys
cat ~/.ssh/id_rsa.pub > /srv/salt/users/authorized_keys_for_removal
sed -i 's/password: .*$/password: default/' /srv/pillar/traffic_ops.sls
sed '/start/i\ exit 0' -i  /srv/salt/trafficserver/centos_parameter
sed '/start/i\ exit 0' -i  /srv/salt/ring_buffer/ifup-local


echo "==========================step 2 run AC8 sample case=========================="
cd /root/OMD/automation
git checkout director-3.5.x
#git pull
echo "run first case testHttpRoutingHttpProtocolVodNational"

py.test -s  director/tests/edit/test_ds.py   --testbed-yaml=/root/OMD/automation/testbed_ac8.yaml  --testbed-id=${TESTBED_ID}  \
--debug-level=info --cleanup-volumes=true -k testHttpRoutingHttpProtocolVodNational  >  /tmp/upgrade_case.log
ct_salt_master="crdc-${TESTBED_ID}-cp-director-salt-master"
ct_ops="crdc-${TESTBED_ID}-cp-director-traffic-ops"
opsPort=`docker ps |grep ops|awk '{print $(NF-1)}'| awk -F '->'  '{print$1}' | awk -F ':'  '{print$2}'`
ct_dns="crdc-${TESTBED_ID}-cp-director-dns"


if [[ $? -ne 0 ]]; then
	echo "prepare ac8 testbed failed"
	exit 1
fi

#case list
py.test -s director/tests/upgrade/test_migrate_NGB.py --testbed-yaml=/root/OMD/automation/testbed_ac8.yaml  --testbed-id=${TESTBED_ID} --skip-down=true --skip-setup=true  --skip-prepare=true
if [[ $? -ne 0 ]]; then
	echo "run case test_migrate_NGB failed"
	exit 1
fi


echo "prepare ac8 testbed finished"


echo "==========================step 3 do salt script to config salt-minion=========================="
updateSaltCfg ${TESTBED_ID} ops
dockercmd $ct_salt_master "salt '*ops*'    state.highstate"


echo "==========================step 4  prepare AC9 testbed=========================="
cp -f /root/AC9/${new_omd_salt_rpm} /tmp/
cp -f /root/AC9/${new_omd_core_rpm} /tmp/
cd ${wspath}
./install_rpm.sh ${new_omd_salt_rpm}
./install_rpm.sh ${new_omd_core_rpm}
docker cp /root/AC9/${new_omd_salt_rpm} crdc-${TESTBED_ID}-cp-director-salt-master:/root/
docker cp /root/AC9/${new_omd_core_rpm} crdc-${TESTBED_ID}-cp-director-salt-master:/root/
dockercmd ${ct_salt_master} "yum upgrade  -y  /root/$new_omd_salt_rpm" || echo " "
dockercmd ${ct_salt_master} "yum install  -y /root/$new_omd_core_rpm"  || echo " "
cat ~/.ssh/id_rsa.pub > /srv/salt/users/authorized_keys
cat ~/.ssh/id_rsa.pub > /srv/salt/users/authorized_keys_for_removal
cisco_path='/opt/cisco/director/crdc-upgrade-cp/crdc-upgrade-cp-director-salt-master/pillar'
opsIp=`getIp ${ct_ops}`
dnsIp=`getIp crdc-${TESTBED_ID}-cp-director-dns`
monitorIP=`getIp crdc-${TESTBED_ID}-test-cdn-docker-monitor-1`

sed -i 's/password: .*$/password: default/' /srv/pillar/traffic_ops.sls
sed -i 's/password: .*$/password: default/' ${cisco_path}/traffic_ops.sls
sed -i "s/traffic_ops_url: .*$/traffic_ops_url: https:\/\/$opsIp/" /srv/pillar/traffic_ops.sls
sed -i "s/traffic_ops_url: .*$/traffic_ops_url: https:\/\/$opsIp/" ${cisco_path}/traffic_ops.sls
sed -i 's/domain: .*$/domain: cisco.com/' /srv/pillar/dns.sls
sed -i 's/domain: .*$/domain: cisco.com/' ${cisco_path}/dns.sls
sed '/dns_server/{p;:a;N;$!ba;d}'  -i /srv/pillar/dns.sls
sed '/dns_server/{p;:a;N;$!ba;d}'  -i ${cisco_path}/dns.sls
sed -i "/dns_server/a\\    - $dnsIp" /srv/pillar/dns.sls
sed -i "/dns_server/a\\    - $dnsIp" ${cisco_path}/dns.sls
sed -i "s/repo_ip: .*/repo_ip: $repo_ip/" /srv/pillar/repo.sls
sed -i "s/repo_ip: .*/repo_ip: $repo_ip/" ${cisco_path}/repo.sls
sed -i "s/  traffic_monitor:.*/  traffic_monitor: $monitorIP/" /srv/pillar/traffic_monitor.sls
sed -i "s/  traffic_monitor:.*/  traffic_monitor: $monitorIP/" ${cisco_path}/traffic_monitor.sls
sed '/repo_pkg72_path/d' -i /srv/pillar/repo.sls
sed '/start/i\ exit 0' -i  /srv/salt/trafficserver/centos_parameter
sed '/start/i\ exit 0' -i  /srv/salt/ring_buffer/ifup-local
dockercmd ${ct_ops} "mv  /usr/local/share/perl5 /root/"


echo "==========================step 5 do salt to upgrade=========================="
docker exec -i  ${ct_salt_master} /bin/sh -c " salt '*' cmd.run \" sed -i 's/baseurl.*$/baseurl=http:\/\/10.140.105.143\/repo\/extra_rpms_73/' /etc/yum.repos.d/local.repo\" "
docker exec -i  ${ct_salt_master} /bin/sh -c " sed '/repo_pkg72_path/d' -i /srv/pillar/repo.sls"
docker exec -i  ${ct_salt_master} /bin/sh -c " sed -i \"s/10.0.0.20.*$/$dnsIp/\" /srv/pillar/dns.sls"
docker exec -i  ${ct_salt_master} /bin/sh -c " sed 's/repo_ip.*/repo_ip: 10.140.105.143/' -i /srv/pillar/repo.sls"
rm -f /srv/pillar/*
cp -f  ${cisco_path}/* /srv/pillar/


rm -f /srv/pillar/*
cp -f  ${cisco_path}/* /srv/pillar/

doSalt ${TESTBED_ID}


dockercmd ${ct_ops} "mv /opt/traffic_ops/app/conf/production/riak.conf /opt/traffic_ops/app/conf/production/riak.conf.bak"
dockercmd ${ct_ops} "cat>/opt/traffic_ops/app/conf/production/riak.conf<<EOF
{
    \"user\": \"admin\",
    \"password\": \"default\"
}
EOF
"

#dockercmd ${ct_ops} "mv /opt/traffic_ops/app/local /opt/traffic_ops/app/local.bak"
#docker cp /tmp/local.tar ${ct_ops}:/opt/traffic_ops/app/
#dockercmd ${ct_ops} "tar xf /opt/traffic_ops/app/local.tar -C /opt/traffic_ops/app/"
dockercmd ${ct_ops} "systemctl restart traffic_ops"
dockercmd ${ct_ops} "rm -f /opt/traffic_ops/app/public/CRConfig-Snapshots/test-cdn/CRConfig.json"
dockercmd ${ct_ops} "rm -f /tmp/ops_bkup*"

cd /root/upgrade
echo "==========================step 6 run sanity case for TC2.1=========================="

python update_ops.py  --host=${docker_compose_ip} --port=${opsPort}
docker exec -i  ${ct_salt_master} /bin/sh -c " salt '*edge*' cmd.run 'systemctl restart trafficserver' "
docker exec -i  ${ct_salt_master} /bin/sh -c " salt '*mid*' cmd.run 'systemctl restart trafficserver' "

docker exec -i  ${ct_salt_master} /bin/sh -c " salt '*edge*' cmd.run 'systemctl restart trafficserver' "
docker exec -i  ${ct_salt_master} /bin/sh -c " salt '*mid*' cmd.run 'systemctl restart trafficserver' "

cd /root/OMD/automation
git checkout .
git checkout director
#git pull

#case list
py.test -s director/tests/upgrade/test_migrate_NGB.py --testbed-yaml=/root/OMD/automation/testbed_ac9.yaml  --testbed-id=${TESTBED_ID} --skip-down=true --skip-setup=true  --skip-prepare=true
if [[ $? -ne 0 ]]; then
    echo "run case test_migrate_NGB failed"
    exit 1
fi


exit 0



/bin/cp -f /etc/resolv.conf.bkup /etc/resolv.conf || /bin/true
/bin/cp -f /etc/hosts.bkup  /etc/hosts


echo "=================================clear report======================================"
cd ${wspath}
mkdir -p test_result
cd test_result
rm -f *.xml
cp $cipath/reports/*.xml .