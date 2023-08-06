# Copyright 2011 Gilt Groupe, INC
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
mothership.xen
for interacting with the Citrix XenAPI

requires the XenServer Python module:
http://community.citrix.com/cdn/xs/sdks/
"""

import re
import sys
import time
import socket
import XenAPI
import mothership
import mothership.validate
from pprint import pprint

class XenServerAPIError(Exception):
    pass

class XenServerAPI:
    def __init__(self, cfg, host, user, passwd):
        try:
            unqdn = mothership.validate.v_get_fqn(cfg, host)
            hostname,realm,site_id,domain = mothership.validate.v_split_fqn(cfg, unqdn)
            self.session = XenAPI.Session('https://%s:443' % unqdn)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/__init__: %s" % e)
        try:
            self.session.xenapi.login_with_password(user, passwd)
        except XenAPI.Failure, e:
            # If slave host from pool chosed, contact master
            exec 'err=%s' % str(e)
            self.session = XenAPI.Session('https://%s:443' % err[1])
            self.session.xenapi.login_with_password(user, passwd)
        except socket.error, e:
            try:
                # Try specified host if unqdn fails
                self.session = XenAPI.Session('https://%s:443' % host)
                self.session.xenapi.login_with_password(user, passwd)
            except socket.error, e:
                try:
                    # Try mgmt if connection refused
                    mgmtunqdn = "%s.mgmt.%s.%s.%s" % (hostname, realm, site_id, domain)
                    self.session = XenAPI.Session('https://%s:443' % mgmtunqdn)
                    self.session.xenapi.login_with_password(user, passwd)
                except Exception, e:
                    raise XenServerAPIError("Error in mothership.xen/XenServerAPI/__init__: management hostname not found: %s\nError: %s" % (mgmtunqdn, e))
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/__init__: %s" % e)
        self.specs = {}

    def byte_unit(self, value, multiplier):
        try:
            return int(float(value) * (1024 ** multiplier))
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/byte_unit: %s" % e)

    def view_layout(self):
        try:
            if not self.specs:
                self.get_specs()
            s = self.specs  # to make dict expansion smaller
            for h in s.keys():
                if h == 'off': continue
                print '===== %s =====\tfree\ttotal' % s[h]['name']
                for i in ['cores', 'ram']:
                    print '%20s\t%4d\t%4d' % (i, s[h][i]['free'], s[h][i]['total'])
                for d in s[h]['disk']:
                    if d.startswith('OpaqueRef'):
                        print '%20s\t%4d\t%4d' % (s[h]['disk'][d]['name'],
                            s[h]['disk'][d]['free'], s[h]['disk'][d]['total'])
                print '  VMs:'
                for v in s[h]['vm']:
                    print '%20s\t%2d core(s)' % (
                        s[h]['vm'][v]['name'], s[h]['vm'][v]['cores'])
            if 'off' in s.keys():
                print '===== halted VMs ====='
                for v in s['off']['vm']:
                    print '%20s' % s['off']['vm'][v]['name']
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/view_layout: %s" % e)

    def get_specs(self):
        try:
            sys.stderr.write('Retrieving host specifications\n')
            self.get_pool_hosts()
            self.get_ram()
            self.get_cores()
            self.get_disk()
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_specs: %s" % e)

    def get_pool_hosts(self):
        try:
            vms = []
            for h in self.session.xenapi.host.get_all():
                self.specs[h] = {'name': self.session.xenapi.host.get_hostname(h)}
                self.specs[h]['vm'] = {}
                for vm in self.session.xenapi.host.get_resident_VMs(h):
                    self.specs[h]['vm'][vm] = {}
                    vms.append(vm)
            all = self.session.xenapi.VM.get_all_records()
            for vm in all:
                if vm in vms or all[vm]['is_a_template'] \
                    or all[vm]['is_control_domain']:
                    continue
                if 'off' not in self.specs.keys():
                    self.specs['off'] = {'name': 'halted'}
                    self.specs['off']['vm'] = {}
                self.specs['off']['vm'][vm] = {'name': all[vm]['name_label']}
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_pool_hosts: %s" % e)

    def get_license_expiration(self):
        try:
            for h in self.specs.keys():
                if h == 'off': continue
                self.specs[h]['expires'] = \
                    (int(time.strftime('%s', time.strptime(
                        self.session.xenapi.host.get_license_params(h)['expiry'],
                        '%Y%m%dT%H:%M:%SZ'))) - int(time.time()))/86400
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_license_expiration: %s" % e)

    def get_ram(self):
        try:
            for h in self.specs.keys():
                if h == 'off': continue
                m = self.session.xenapi.host.get_metrics(h)
                self.specs[h]['ram'] = {
                    'free': self.byte_unit(
                        self.session.xenapi.host_metrics.get_memory_free(m), -3),
                    'total': self.byte_unit(
                        self.session.xenapi.host_metrics.get_memory_total(m), -3)
                    }
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_ram: %s" % e)

    def get_cores(self):
        try:
            for h in self.specs.keys():
                if h == 'off': continue
                used = 0
                for v in self.specs[h]['vm'].keys():
                    name = self.session.xenapi.VM.get_record(v)['name_label']
                    cpus = self.session.xenapi.VM.get_record(v)['VCPUs_max']
                    if name.startswith('Control'):
                        self.specs[h]['cores'] = {}
                        self.specs[h]['cores']['total'] = int(cpus)
                        del self.specs[h]['vm'][v]
                    else:
                        self.specs[h]['vm'][v]['name'] = name
                        self.specs[h]['vm'][v]['cores'] = int(cpus)
                        used += int(cpus)
                self.specs[h]['cores']['used'] = used
                self.specs[h]['cores']['free'] = self.specs[h]['cores']['total'] - used
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_cores: %s" % e)

    def get_disk(self):
        try:
            for h in self.specs.keys():
                if h == 'off': continue
                self.specs[h]['disk'] = {}
                self.specs[h]['disk']['free'] = 0
                for p in self.session.xenapi.host.get_PBDs(h):
                    s = self.session.xenapi.PBD.get_SR(p)
                    self.specs[h]['disk'][s] = {}
                    self.specs[h]['disk'][s]['name'] = self.session.xenapi.SR.get_name_label(s)
                    self.specs[h]['disk'][s]['total'] = self.byte_unit(
                        self.session.xenapi.SR.get_physical_size(s), -3)
                    if self.specs[h]['disk'][s]['total'] == 0 or \
                        'ISO' in self.specs[h]['disk'][s]['name']:
                        del self.specs[h]['disk'][s]
                        continue
                    free = self.specs[h]['disk'][s]['total'] - self.byte_unit(
                        self.session.xenapi.SR.get_physical_utilisation(s), -3)
                    self.specs[h]['disk'][s]['free'] = free
                    if free > self.specs[h]['disk']['free']:
                        self.specs[h]['disk']['free'] = free
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_disk: %s" % e)

    def filter_hosts(self, key, need=None):
        try:
            if not key:
                return
            for h in self.specs.keys():
                if h == 'off': continue
                if self.specs[h][key]['free'] < need:
                    del self.specs[h]
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/filter_hosts: %s" % e)

    def check_license(self, host):
        try:
            if not self.specs:
                self.get_pool_hosts()
                self.get_license_expiration()
            for h in self.specs.keys():
                if h == 'off': continue
                if self.specs[h]['name'] == host.split('.')[0]:
                    print 'License for %s expires in %s day(s)' % (
                        host, self.specs[h]['expires'])
                    return
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/check_license: %s" % e)

    def triple_check(self, info):
        try:
            if not self.specs:
                self.get_specs()
            for i in ['cores', 'ram', 'disk']:
                self.filter_hosts(key=i, need=info[i])
                if len(self.specs) == 1 and 'off' in self.specs:
                    print 'Xen server/pool has insufficient %s to provision VM' % i
                    return False, False
            host, ref = self.choose_storage(info['disk'])
            if not host:
                host = info['power_switch']
            if '.' not in host:
                # make sure unqdn is returned
                host = '%s.%s.%s' % (host, info['realm'], info['site_id'])
            return host, ref
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/triple_check: %s" % e)

    def choose_storage(self, need=None, force_xenhost=None):
        '''Checks all disks for available space and returns xenhost, OpaqueRef.
           Optionally accept xenhost to force selection on a particular host'''
        try:
            if not self.specs:
                self.get_specs()
            storage = {}
            for h in self.specs.keys():
                if h == 'off': continue
                host = self.specs[h]
                if force_xenhost is not None and not host['name'].startswith(force_xenhost):
                    continue
                for s in host['disk'].keys():
                    if not s.startswith('OpaqueRef'):
                        continue
                    if need > host['disk'][s]['free']:
                        continue
                    item = '%5d GB disk free' % host['disk'][s]['free']
                    if host['disk'][s]['name'].startswith('Local'):
                        item = '%11s: %-22s (%s, %2d cpu(s) %2d GB ram avail)' % (
                            host['name'], host['disk'][s]['name'], item,
                            host['cores']['free'], host['ram']['free'])
                    else:
                        item = '%-35s (%s)' % (host['disk'][s]['name'], item)
                    if not s in storage.keys():
                        storage[s] = item
            if len(storage) > 1:
                for s in storage.values():
                    print '%d) %s' % (storage.values().index(s), s)
                ans = raw_input('Which do you want to use: ')
            else:
                ans = 0
            if int(ans) < 0 or int(ans) >= len(storage.values()):
                print 'Storage selection aborted.'
                return None, False
            else:
                #print 'User selected "%s"' % storage.keys()[int(ans)]
                if 'Local' in storage.values()[int(ans)]:
                    xenhost = storage.values()[int(ans)].split(':')[0].replace(' ', '')
                else:
                    xenhost = None
                if force_xenhost is not None:
                    xenhost = force_xenhost
                return xenhost, storage.keys()[int(ans)]
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/choose_storage: %s" % e)

    def get_refs(self, host):
        try:
            if not self.specs:
                self.get_specs()
            vmhost = None
            xenhost = None
            for h in self.specs.keys():
                for v in self.specs[h]['vm']:
                    if self.specs[h]['vm'][v]['name'] == host:
                        #print 'VM %s found on %s' % (host, self.specs[h]['name'])
                        vmhost = v
                        xenhost = h
                        break
            if not xenhost:
                sys.stderr.write('%s is not running on any xenserver\n' % host)
                sys.exit(0)
            return xenhost, vmhost
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/get_refs: %s" % e)

    def resize_vm(self, info, opts):
        try:
            if 'server' in info.keys():
                info = info['server'][0]
            xenhost, vmhost = self.get_refs(info['hostname'])
            xenapi = self.session.xenapi
            vdi = xenapi.VBD.get_VDI(xenapi.VM.get_VBDs(vmhost)[0])
            self.specs[xenhost]['disk']['free'] = \
                self.specs[xenhost]['disk'][xenapi.VDI.get_SR(vdi)]['free']
            for i in ['cores', 'ram', 'disk']:
                if getattr(opts, i):
                    if int(getattr(opts, i)) > \
                        (self.specs[xenhost][i]['free'] + info[i]):
                        sys.stderr.write('%s has insufficient %s to resize VM\n' % (
                            self.specs[xenhost]['name'], i))
                        return False
                    #print 'Testing %s: %s -> %s (%s currently avail)' % (i,
                    #    info[i], getattr(opts, i),
                    #    self.specs[xenhost][i]['free'])
            setattr(opts, 'force', True)
            self.shutdown_vm(info, opts)
            for i in ['cores', 'ram', 'disk']:
                if not getattr(opts, i):
                    continue
                if i == 'disk':
                    vref = vdi
                else:
                    vref = vmhost
                exec 'self.resize_%s(vref, getattr(opts, "%s"))' % (i, i)
            self.start_vm(info, opts)
            return True
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/resize_vm: %s" % e)

    def shutdown_vm(self, info, opts):
        try:
            if 'server' in info.keys():
                info = info['server'][0]
            xenhost, vmhost = self.get_refs(info['hostname'])
            xenapi = self.session.xenapi
            vmdict = xenapi.VM.get_record(vmhost)
            if vmdict['power_state'] != 'Halted':
                if not opts.force:
                    ans = raw_input('Are you sure you wish to shutdown %s (y/N)? '\
                        % info['hostname'])
                    if ans.lower() != 'y':
                        print 'Shutdown VM aborted.'
                        sys.exit(1)
                sys.stderr.write('Shutting down %s\n' % info['hostname'])
                xenapi.VM.clean_shutdown(vmhost)
            else:
                sys.stderr.write('%s already stopped\n' % info['hostname'])
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/shutdown_vm: %s" % e)

    def start_vm(self, info, opts):
        try:
            if 'server' in info.keys():
                info = info['server'][0]
            xenapi = self.session.xenapi
            vmhost = xenapi.VM.get_by_name_label(info['hostname'])[0]
            vmdict = xenapi.VM.get_record(vmhost)
            if vmdict['power_state'] != 'Running':
                sys.stderr.write('Starting up %s\n' % info['hostname'])
                xenapi.VM.start(vmhost, False, True)
            else:
                sys.stderr.write('%s already running\n' % info['hostname'])
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/start_vm: %s" % e)

    def resize_cores(self, vref, value):
        try:
            xenapi = self.session.xenapi
            vmdict = xenapi.VM.get_record(vref)
            oldval = int(vmdict['VCPUs_max'])
            print 'Resizing cores from %s to %s' % (oldval, value)
            if oldval < int(value):
                xenapi.VM.set_VCPUs_max(vref, value)
            xenapi.VM.set_VCPUs_at_startup(vref, value)
            if oldval > int(value):
                xenapi.VM.set_VCPUs_max(vref, value)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/resize_cores: %s" % e)

    def resize_ram(self, vref, value):
        try:
            xenapi = self.session.xenapi
            vmdict = xenapi.VM.get_record(vref)
            oldval = self.byte_unit(vmdict['memory_static_max'], -3)
            print 'Resizing ram from %s to %s' % (oldval, value)
            mem = str(self.byte_unit(value, 3))
            xenapi.VM.set_memory_limits(vref, mem, mem, mem, mem)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/resize_ram: %s" % e)

    def resize_disk(self, vref, value):
        try:
            xenapi = self.session.xenapi
            oldval = xenapi.VDI.get_virtual_size(vref)
            if self.byte_unit(value, 3) < int(oldval):
                sys.stderr.write('Shrinking virtual disk is not allowed\n')
                sys.stderr.write('!! Skipping virtual disk resizing !!\n')
            else:
                print 'Resizing disk from %s to %s' % (
                    self.byte_unit(oldval, -3), int(value))
                xenapi.VDI.resize(vref, str(
                    self.byte_unit(value, 3)))
                sys.stderr.write('!! You must run the necessary fdisk/lvm commands for the OS to recognize the changes !!\n')
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/resize_disk: %s" % e)

    def delete_vm(self, info, opts):
        try:
            if 'server' in info.keys():
                info = info['server'][0]
            if not opts.force:
                ans = raw_input('Are you sure you wish to delete %s (y/N)? ' \
                    % info['hostname'])
                if ans.lower() != 'y':
                    print 'Destroy VM aborted.'
                    sys.exit(1)
            xenhost, vmhost = self.get_refs(info['hostname'])
            xenapi = self.session.xenapi
            try:
                vdi = xenapi.VBD.get_VDI(xenapi.VM.get_VBDs(vmhost)[0])
            except:
                vdi = False
            self.shutdown_vm(info, opts)
            sys.stderr.write('Destroying %s VM\n' % info['hostname'])
            xenapi.VM.destroy(vmhost)
            if vdi:
                sys.stderr.write('Destroying %s VDI\n' % info['hostname'])
                xenapi.VDI.destroy(vdi)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/delete_vm: %s" % e)

    def install_vm(self, info, opts):
        try:
            if not self.specs:
                self.get_specs()
            vmexists = False
            for h in self.specs.keys():
                for v in self.specs[h]['vm'].keys():
                    name = self.session.xenapi.VM.get_record(v)['name_label']
                    if name == info['server'][0]['hostname']:
                        sys.stderr.write('%s already exists on xenserver\n' % name)
                        vmexists = True
                        break
            if vmexists:
                sys.stderr.write('!! Aborting install_vm process !!\n')
                sys.exit(1)
            vmhost = self.create_vm(info)
            vdi = self.create_vdi(info)
            vbd = self.create_vbd(vmhost, vdi)
            if not self.create_vif(vmhost, info):
                self.session.xenapi.VM.destroy(vmhost)
            else:
                self.start_vm(info, opts)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/install_vm: %s" % e)

    def create_vbd(self, vmhost, vdi):
        try:
            data = {'VDI': vdi, 'VM': vmhost, 'bootable': True,
                'empty': False, 'mode': 'RW', 'other_config': {'owner': ''},
                'qos_algorithm_params': {}, 'qos_algorithm_type': '',
                'type': 'Disk', 'unpluggable': False, 'userdevice': '0'}
            return self.session.xenapi.VBD.create(data)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/create_vbd: %s" % e)

    def create_vdi(self, info):
        try:
            data = {'SR': info['server'][0]['storage'],
                'virtual_size': str(self.byte_unit(info['server'][0]['disk'], 3)),
                'name_description': 'Created by XenServer API',
                'name_label': info['server'][0]['hostname'],
                'other_config': {}, 'read_only': False,
                'sharable': False, 'type': 'system'}
            return self.session.xenapi.VDI.create(data)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/create_vdi: %s" % e)

    def create_vm(self, info):
        try:
            #for i in info['network']:
            #    if i['interface'] == 'eth0':
            #        net = i
            mem = str(self.byte_unit(info['server'][0]['ram'], 2))
            data = { 'HVM_boot_params': {}, 'HVM_boot_policy': '',
                'HVM_shadow_multiplier': 1.0, 'PCI_bus': '',
                # For DHCP omit the ip/netmask/gateway and use default:
                'PV_args': 'ks=%s/%s ksdevice=eth0 noipv6 utf8' % (
                    info['kick']['ks'], info['server'][0]['hostname']),
                # Use static ip/netmask instead of DHCP
                #'PV_args': 'ks=%s/%s ksdevice=eth0 noipv6 utf8 ip=%s netmask=%s' \
                #    % (info['kick']['ks'], info['server'][0]['hostname'],
                #    net['ip'], net['netmask']),
                'PV_bootloader': 'eliloader', 'PV_bootloader_args': '',
                'PV_kernel': '', 'PV_legacy_args': '', 'PV_ramdisk': '',
                'VCPUs_params': {}, 'VCPUs_at_startup': '1',
                'VCPUs_max': str(info['server'][0]['cores']),
                'actions_after_crash': 'restart',
                'actions_after_reboot': 'restart',
                'actions_after_shutdown': 'destroy',
                'affinity': 'OpaqueRef:NULL',
                'allowed_operations': ['changing_dynamic_range',
                    'pool_migrate', 'changing_VCPUs_live', 'suspend',
                    'hard_reboot', 'hard_shutdown', 'clean_reboot',
                    'clean_shutdown', 'pause', 'checkpoint', 'snapshot'],
                'ha_always_run': False, 'is_a_snapshot': False,
                'is_a_template': False, 'is_control_domain': False,
                'memory_dynamic_max': mem, 'memory_dynamic_min': mem,
                'memory_static_max': mem, 'memory_target': mem,
                'memory_overhead': '%s' % self.byte_unit(1, 2),
                'memory_static_min': '%s' % self.byte_unit(512, 2), 
                'name_description': 'Installed via XenServer API',
                'name_label': info['server'][0]['hostname'],
                'other_config': {'install-distro': 'rhlike',
                    'install-methods': 'cdrom,nfs,http,ftp',
                    'install-repository': info['kick']['repo'],
                    'linux_template': 'true',
                    'mac_seed': '225833d5-9652-8af5-df7f-c7f75da7971a',
                    'rhel5': 'true'},
                'platform': {'acpi': 'true', 'apic': 'true',
                  'nx': 'false', 'pae': 'true', 'viridian': 'true'},
                'recommendations': '<restrictions>' +
                    '<restriction field=memory-static-max max=17179869184 />' +
                    '<restriction field=vcpus-max max=8 />' +
                    '<restriction property=number-of-vbds max=7 />' +
                    '<restriction property=number-of-vifs max=7 /></restrictions>',
                'user_version': '1'}
            return self.session.xenapi.VM.create(data)
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/create_vm: %s" % e)

    def create_vif(self, vmhost, info):
        try:
            pifs = self.session.xenapi.PIF.get_all_records()
            nics = ['eth0', 'bond0']
            for n in nics:
                #print 'eth%d -> %s' % (nics.index(n), n)
                mac = None
                network = None
                for p in pifs.keys():
                    if pifs[p]['device'] == n:
                        network = pifs[p]['network']
                        break
                if not network:
                    sys.stderr.write('Unable to find %s network on xenserver\n' % n)
                    return False
                for i in info['network']:
                    if i['interface'] == 'eth%d' % nics.index(n):
                        mac = i['mac']
                        break
                if not mac:
                    sys.stderr.write('Unable to find %s mac in cobbler\n' % n)
                    return False
                data = { 'VM': vmhost, 'MAC': mac, 'MAC_autogenerated': False,
                    'MTU': '1500', 'allowed_operations': ['attach', 'unplug'],
                    'current_operations': {}, 'device': str(nics.index(n)),
                    'network': network, 'other_config': {},
                    'qos_algorithm_params': {}, 'qos_algorithm_type': '',
                    'qos_supported_algorithms': [], 'runtime_properties': {},
                    'status_code': '0', 'status_detail': ''}
                self.session.xenapi.VIF.create(data)
            return True
        except Exception, e:
            raise XenServerAPIError("Error in mothership.xen/XenServerAPI/create_vif: %s" % e)

# CLI: xe vm-import sr-uuid=<SR-UID> filename=<PATH-TO-XVA>
#    def import_xva(self, filename):
#        self.session.xenapi.VM.import()
# apparently, the XMLRPC API has no import or export methods
