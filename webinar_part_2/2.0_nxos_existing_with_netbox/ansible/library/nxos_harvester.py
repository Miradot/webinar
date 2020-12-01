from ansible.module_utils.basic import *
import re
import yaml
import requests
import pynetbox

# used in demo scenario because vNXOS has 128 interfaces
ALLOWED_INTERFACES = [
    "Ethernet1/1",
    "Ethernet1/2",
    "Ethernet1/3",
    "Ethernet1/4",
    "Ethernet1/5",
    "Ethernet1/6",
    "mgmt0"
]


def nb_get_conn(nb_url, nb_token):
    """ used to get a connection pipe to netbox """
    return pynetbox.api(url=nb_url, token=nb_token)


def nb_configurator(filename, nb, new_nxos_config):
    """ configures netbox with harvested information """
    try:
        nb.dcim.devices.create(
            name=new_nxos_config["hostname"],
            device_type=1 if new_nxos_config["type"] == "N9K-C93180YC-FX" else 1,
            device_role=1 if "spine" in new_nxos_config["hostname"] else 2,
            site=1,
        )
    except pynetbox.core.query.RequestError: # if the device already exists, move on
        pass

    for k, v in new_nxos_config["interfaces"].items():
        try:
            interface = nb.dcim.interfaces.get(name=k, device=new_nxos_config["hostname"])
            interface.description = v["description"]

            if v["vlan_id"] and not nb.ipam.vlans.get(vid=v["vlan_id"]):
                nb.ipam.vlans.create(vid=v["vlan_id"], name=v["vlan_name"], site=1)

            if v["vlan_id"]:
                interface.mode = v["mode"]
                nb_vlan = nb.ipam.vlans.get(vid=v["vlan_id"])
                interface.untagged_vlan = nb_vlan.id

            if v["ipv4"] and not nb.ipam.ip_addresses.get(address=v["ipv4"]):
                nb.ipam.ip_addresses.create(address=v["ipv4"], status=1, interface=interface.id)

            if k == "mgmt0" and v["ipv4"]:
                device = nb.dcim.devices.get(name=new_nxos_config["hostname"])
                ip = nb.ipam.ip_addresses.get(q=v["ipv4"])
                device.primary_ip4 = ip.id
                device.save()

            interface.save()

        except pynetbox.core.query.RequestError as e:
            print(e.error)

    # delete following from dict, we want to handle this from netbox
    del new_nxos_config["interfaces"]
    del new_nxos_config["type"]
    del new_nxos_config["hostname"]

    # rewrite the file with deleted variables
    with open(filename, "w") as file:
        yaml.dump(new_nxos_config, file)


def read_nxos_config(filename):
    """ opens up and reads information from the gatherer ansible file """
    with open(filename) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def get_nxos_info(hostname, username, password, nxapi_port, command):
    """ sends commands to nxos and returns the response """
    data = [
        {
            "jsonrpc": "2.0",
            "method": "cli",
            "params": {
                "cmd": command,
                "version": 1
            },
            "id": 1
        }
    ]

    response = requests.post("http://{}:{}/ins".format(hostname, nxapi_port),
                             auth=(username, password),
                             data=json.dumps(data),
                             headers={"content-type": "application/json-rpc"})

    return response.json()


def nxos_harvester(filename, hostname, username, password, nxapi_port):
    """ harvests and parses information from nxos api directly """

    new_nxos_config = dict()
    interface_vlans = dict()

    vlans = get_nxos_info(hostname, username, password, nxapi_port,
        "show vlan brief")["result"]["body"]["TABLE_vlanbriefxbrief"]["ROW_vlanbriefxbrief"]

    for interface in ALLOWED_INTERFACES:
        interface_vlans[interface] = dict()

        if type(vlans) == list:
            for vlan in vlans:
                try:
                    if interface in vlan["vlanshowplist-ifidx"]:
                        interface_vlans[interface]["vlan_id"] = str(vlan["vlanshowbr-vlanid"])
                        interface_vlans[interface]["vlan_name"] = str(vlan["vlanshowbr-vlanname"])
                except KeyError: # if KeyError interface does not exist in the vlan-interface list, ignore and move on
                    pass
        elif type(vlans) == dict:
            if interface in vlans["vlanshowplist-ifidx"]:
                interface_vlans[interface]["vlan_id"] = str(vlans["vlanshowbr-vlanid"])
                interface_vlans[interface]["vlan_name"] = str(vlans["vlanshowbr-vlanname"])

    bgp_neighbor_list = list()

    try:
        for line in get_nxos_info(hostname,
                                  username,
                                  password,
                                  nxapi_port,
                                  "show bgp all neigh")["result"]["body"]["TABLE_neighbor"]["ROW_neighbor"]:

            bgp = dict()
            bgp["neighbor"] = str(line["neighbor"])
            bgp["remoteas"] = str(line["remoteas"])

            bgp["afi"] = str(line["TABLE_peraf"]["ROW_peraf"]["TABLE_persaf"]["ROW_persaf"]["per-af-name"]).split(" ")[0].lower()
            bgp["safi"] = str(line["TABLE_peraf"]["ROW_peraf"]["TABLE_persaf"]["ROW_persaf"]["per-af-name"]).split(" ")[1].lower()

            bgp_neighbor_list.append(bgp)
    except:
        pass

    bgp_system_list = list()

    try:
        output = get_nxos_info(hostname , username, password, nxapi_port, "show bgp session")
        bgp = dict()
        bgp["localas"] = str(output["result"]["body"]["localas"])
        bgp["routerid"] = str(output["result"]["body"]["TABLE_vrf"]["ROW_vrf"]["router-id"])
        bgp_system_list.append(bgp)
    except:
        pass

    new_nxos_config["bgpneighbors"] = bgp_neighbor_list
    new_nxos_config["bgpsystem"] = bgp_system_list

    with open(filename, "w") as file:
        yaml.dump(new_nxos_config, file)

    return interface_vlans


def nxos_parser(filename, nxos_config, interface_vlans):
    """ parse information from original file """

    new_nxos_config = dict()
    interfaces = dict()

    new_nxos_config["hostname"] = nxos_config["net_hostname"]
    new_nxos_config["features"] = nxos_config["net_features_enabled"]

    if nxos_config["net_platform"] == "N9K-9000v":
        new_nxos_config["type"] = "N9K-C93180YC-FX"
    else:
        new_nxos_config["type"] = ""

    new_nxos_config["ntp"] = list()
    for ntp_server in re.findall(r'ntp (.+) (.+)', nxos_config['net_config']):
        new_nxos_config["ntp"].append(ntp_server[0].split(" ")[1])

    try:
        new_nxos_config["dns"] = re.search(r'name-server (.+)', nxos_config['net_config']).group(1).split(" ")
    except AttributeError:
        new_nxos_config["dns"] = None

    for interface_key, interface_val in nxos_config["net_interfaces"].items():
        if interface_key in ALLOWED_INTERFACES:
            interfaces[interface_key] = dict()
            try:
                interfaces[interface_key]["description"] = interface_val["description"]
            except KeyError:
                interfaces[interface_key]["description"] = ""

            try:
                interfaces[interface_key]["ipv4"] = interface_val["ipv4"]["address"] + "/" + str(interface_val["ipv4"]["masklen"])
            except KeyError:
                interfaces[interface_key]['ipv4'] = ""

            if interface_vlans.get(interface_key):
                interfaces[interface_key]["mode"] = "access"
                interfaces[interface_key]["vlan_id"] = interface_vlans.get(interface_key)["vlan_id"]
                interfaces[interface_key]["vlan_name"] = interface_vlans.get(interface_key)["vlan_name"]
            else:
                interfaces[interface_key]["mode"] = ""
                interfaces[interface_key]["vlan_id"] = ""
                interfaces[interface_key]["vlan_name"] = ""

    new_nxos_config["interfaces"] = interfaces

    with open(filename, "a") as file:
        yaml.dump(new_nxos_config, file)


def main():
    module = AnsibleModule(argument_spec=dict(
        filename=dict(type="str", required=True),
        hostname=dict(type="str", required=True),
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        nxapi_port=dict(type="str", required=True),
        netbox_url=dict(type="str", required=True),
        mode=dict(type="str", required=True),
        netbox_token=dict(type="str", required=True, no_log=True)))

    nxos_config = read_nxos_config(module.params["filename"])

    interface_vlans = nxos_harvester(module.params["filename"],
            module.params["hostname"],
            module.params["username"],
            module.params["password"],
            module.params["nxapi_port"])

    nxos_parser(module.params["filename"], nxos_config, interface_vlans)

    nxos_config = read_nxos_config(module.params["filename"])

    if module.params["mode"] == "get":
        nb = nb_get_conn(module.params["netbox_url"], module.params["netbox_token"])
        nb_configurator(module.params["filename"], nb, nxos_config)

    module.exit_json()


if __name__ == "__main__":
    main()
