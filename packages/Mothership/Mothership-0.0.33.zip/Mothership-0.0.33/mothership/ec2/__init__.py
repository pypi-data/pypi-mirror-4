# Copyright 2013 Gilt Groupe, INC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
    mothership.ec2

    Package for interacting with EC2
"""

import time

import mothership
from mothership.mothership_models import *
import boto.ec2

try:
    import json
except ImportError:
    import simplejson as json


conn = None
def get_connection(cfg):
    global conn
    if conn is None:
        conn = boto.ec2.connect_to_region(cfg.ec2_region,
                    aws_access_key_id=cfg.aws_access_key,
                    aws_secret_access_key=cfg.aws_secret_key)
    return conn


def mothership_cmd(cfg, subcmd, opts):
    conn = get_connection(cfg)

    if opts.list is not False:
        print '%-20s %-10s %s' % ('name', 'state', 'launched')
        print '%-20s %-10s %s' % ('-'*20, '-'*10, '-'*8)
        for instance in list_instances(conn, opts):
            name = instance.tags.get('Name', None)
            state = instance.state
            launch_time = '-'
            if state == 'running':
                launch_time = instance.launch_time
            print '%-20s %-10s %s' % (name, state, launch_time)
    elif opts.init is not None:
        init_instances(conn, opts, cfg)
    elif opts.start is not None:
        start_instances(conn, opts)
    elif opts.stop is not None:
        stop_instances(conn, opts)
    elif opts.terminate is not None:
        terminate_instances(conn, opts)
    pass


def _get_ip_address(cfg, hostname, interface):
    """return an ip address given an hostname and an interface."""
    host, realm, site_id = mothership.get_unqdn(cfg, hostname)

    h, s = cfg.dbsess.query(Hardware, Server).filter(Server.hostname==host).\
            filter(Server.realm==realm).\
            filter(Server.site_id==site_id).\
            filter(Hardware.hw_tag==Server.hw_tag).first()

    for n in cfg.dbsess.query(Network).\
            filter(Network.server_id==s.id).\
            filter(Network.interface==interface).all():
        yield n.ip


# map hostname => Instance
_namecache = {}
def _instance_from_hostname(conn, name):
    if name in _namecache:
        return _namecache.get(name)

    for instance in list_instances(conn, None):
        tag_name = instance.tags.get('Name', '')
        _namecache[tag_name] = instance
        if tag_name == name:
            return instance
    else:
        return None


def init_instances(conn, opts, cfg):
    hostnames = opts.init.split(',')
    for hostname in hostnames:
        private_ip_address = _get_ip_address(cfg, hostname, 'eth1').next()
        tags = {'Name': hostname}

        _init(conn, cfg.ec2_image_id, hostname,
            key_pair=cfg.ec2_key_pair,
            security_group_ids=[cfg.ec2_security_group],
            instance_type=cfg.ec2_instance_type, subnet_id=cfg.ec2_subnet_id,
            private_ip_address=private_ip_address, tags=tags)


def _init(conn, image_id, hostname, key_pair=None, security_group_ids=None,
        instance_type=None, subnet_id=None, private_ip_address=None, tags=None):

    def _update_tags(instance, tags):
        for k, v in tags.iteritems():
            instance.add_tag(k, v)

    # fully qualified name is required for puppet autosign to work properly
    if not hostname.endswith('.gilt.local'):
        hostname = hostname + '.gilt.local'

    user_data = {'hostname': hostname}
    user_data = json.dumps(user_data)

    reservation = conn.run_instances(image_id=image_id, key_name=key_pair,
            security_group_ids=security_group_ids, user_data=user_data,
            instance_type=instance_type, subnet_id=subnet_id,
            private_ip_address=private_ip_address)

    pending_launch = reservation.instances[:]

    # if we are quick enough the ec2 API won't know the instance IDs it just
    # returned :(
    time.sleep(2)

    for cycle in range(1, 10):
        for instance in reservation.instances:
            status = instance.update()
            if status == 'running':
                print '%s is running' % instance
                pending_launch.remove(instance)
                _update_tags(instance, tags)
        if len(pending_launch) == 0:
            break
        print '%r pending launch, waiting' % pending_launch
        time.sleep(7)
    else:
        print 'unable to verify instances have launched within the time slot'
        return False

    return True


def list_instances(conn, opts):
    for reservation in conn.get_all_instances():
        for instance in reservation.instances:
            yield instance


def _foreach_instance(conn, action, hostnames):
    ACTION_MAP = {
        'start': conn.start_instances,
        'stop': conn.stop_instances,
        'terminate': conn.terminate_instances,
    }

    instance_list = []

    hostnames = hostnames.split(',')
    for hostname in hostnames:
        instance = _instance_from_hostname(conn, hostname)
        if instance is None:
            print "instance for %s not found, skipping" % hostname
            continue
        instance_list.append(instance)

    if not instance_list:
        print "no instances to act on, exiting"
        return False

    func = ACTION_MAP.get(action, None)
    if func is None:
        print "unable to find action for %s" % action
        return False

    result = func([x.id for x in instance_list])
    print '%s %r' % (action, result)


def start_instances(conn, opts):
    _foreach_instance(conn, "start", opts.start)


def stop_instances(conn, opts):
    _foreach_instance(conn, "stop", opts.stop)


def terminate_instances(conn, opts):
    _foreach_instance(conn, "terminate", opts.terminate)
