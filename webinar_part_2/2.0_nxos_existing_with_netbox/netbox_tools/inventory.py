#!/usr/bin/env python
import pynetbox
import json
from json import JSONEncoder
from netaddr import IPNetwork

URL = ''
TOKEN = ''

class Interface(object):
    def __init__(self):
        self.name = None
        self.vlan_name = None
        self.vlan_id = None
        self.description = None
        self.ipv4 = False
        
    def get_state(self):
        return 'present' if self.vlan_name and self.vlan_id and self.description else 'absent'

    def __str__(self):
        return '{} - {} - {}'.format(self.description, self.vlan_id, self.vlan_name)


class InterfaceEncoder(JSONEncoder):
    def default(self, o):
        data = o.__dict__
        data['state'] = o.get_state()
        return data

def get_conn():
    return pynetbox.api(url=URL, token=TOKEN)

def get_site_list(nb):
    return nb.dcim.sites.all()

def get_devices(nb, site=None):
    if site:
        return nb.dcim.devices.filter(site=site)
    else:
        return nb.dcim.devices.all()

def get_interfaces(nb, device_name, site_name=None):
    if site_name:
        return nb.dcim.interfaces.filter(device=device_name, site=site_name)
    else:
        return nb.dcim.interfaces.filter(device=device_name)

def get_vlans(nb, site_name=None):
    if site_name:
        return nb.ipam.vlans.filter(site=site_name)
    else:    
        return nb.ipam.vlans.all()


def get_interface_reps(interfaces_available):
    td_interface_objs = list()

    for this_interface in interfaces_available:
        this_interface_obj = Interface()
        this_interface_obj.name = this_interface.name
        this_interface_obj.description = this_interface.description

        if this_interface.untagged_vlan:
            this_interface_obj.vlan_name = this_interface.untagged_vlan.name
            this_interface_obj.vlan_id = this_interface.untagged_vlan.vid

        if this_interface.count_ipaddresses:
            this_interface_obj.ipv4 = True

        td_interface_objs.append(this_interface_obj)

    return td_interface_objs

def main():
    nb = get_conn()
    devices = dict()
    processed_serials = list()

    for td_obj in get_devices(nb):
        td_dict = td_obj.__dict__
        td_name = str(td_dict['name'])
        td_site = str(td_dict['site'])
        td_type = str(td_dict['device_type'])
        td_serial = str(td_dict['serial'])
        if td_dict['primary_ip4']:
            td_ip = IPNetwork(str(td_dict['primary_ip4']))
        else:
            td_ip = IPNetwork('1.3.3.7/24')

        # get interfaces
        interfaces_available = get_interfaces(nb, td_name)
        td_interfaces = get_interface_reps(interfaces_available)

        devices[td_name] = {
            'hostname': td_name,
            'sitename': td_site,
            'device_type': td_type,
            'mgmt_ip_address': str(td_ip.ip),
            'mgmt_ip_netmask': str(td_ip.netmask),
            'interfaces': td_interfaces
        }
        processed_serials.append(td_serial)

    print(json.dumps(devices, cls=InterfaceEncoder, indent=4))



if __name__ == '__main__':
    main()

