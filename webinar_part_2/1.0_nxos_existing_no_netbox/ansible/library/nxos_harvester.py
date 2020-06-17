from ansible.module_utils.basic import *
import re
import yaml
import requests

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

    headers = {"content-type": "application/json-rpc"}

    response = requests.post("http://{}:{}/ins".format(hostname, nxapi_port),
                             auth=(username, password),
                             data=json.dumps(data),
                             headers=headers
                             )

    return response.json()


def nxos_harvester(filename, hostname, username, password, nxapi_port):
    """ harvests and parses information from nxos api directly """

    new_nxos_config = dict()
    interface_vlans = dict()

    vlans = get_nxos_info(hostname, username, password, nxapi_port, "show vlan brief")

    for interface in ALLOWED_INTERFACES:
        interface_vlans[interface] = dict()

        for vlan in vlans["result"]["body"]["TABLE_vlanbriefxbrief"]["ROW_vlanbriefxbrief"]:
            try:
                if vlan["vlanshowbr-vlanid"] == ("1" and "100"): # ignore vlan 1 and 100 - 100 is a special vxlan-vlan
                    continue
            except TypeError: # if TypeError this means that vlan 1 is the only vlan existing, therefore just ignore
                continue
            try:
                if interface in vlan["vlanshowplist-ifidx"]:
                    interface_vlans[interface]["vlan_id"] = str(vlan["vlanshowbr-vlanid"])
                    interface_vlans[interface]["vlan_name"] = str(vlan["vlanshowbr-vlanname"])
            except KeyError: # if KeyError interface does not exist in the vlan-interface list, ignore this and move on
                pass

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

            if "L2VPN" in str(line["TABLE_peraf"]["ROW_peraf"]["TABLE_persaf"]["ROW_persaf"]["per-af-name"]):
                bgp["safi"] = "evpn"
                bgp["afi"] = "l2vpn"
            elif "IPv4" in str(line["TABLE_peraf"]["ROW_peraf"]["TABLE_persaf"]["ROW_persaf"]["per-af-name"]):
                bgp["safi"] = "unicast"
                bgp["afi"] = "ipv4"

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

    try:
        new_nxos_config["ntp"] = list()
        for ntp_server in re.findall(r'ntp (.+) (.+)', nxos_config['net_config']):
            new_nxos_config["ntp"].append(ntp_server[0].split(" ")[1])
    except:
        pass

    try:
        for dns_server in re.findall(r'name-server (.+)', nxos_config['net_config']):
            new_nxos_config["dns"] = (dns_server.split(" "))
    except:
        pass

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
        nxapi_port=dict(type="str", required=True)))

    nxos_config = read_nxos_config(module.params["filename"])

    interface_vlans = nxos_harvester(module.params["filename"],
            module.params["hostname"],
            module.params["username"],
            module.params["password"],
            module.params["nxapi_port"])

    nxos_parser(module.params["filename"], nxos_config, interface_vlans)

    module.exit_json()


if __name__ == "__main__":
    main()
