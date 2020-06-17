from ansible.module_utils.basic import *
import yaml
import requests


def read_nxos_config(src_file):
    """ read original file """
    with open(src_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def read_nxos_tmp_config(dst_file):
    """ read the parsed tmp file """
    with open(dst_file) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def get_nxos_info(hostname, username, password, nxapi_port, command):
    """ get information from nxapi """
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
                             headers=headers)

    return response.json()


def differ(hostname, username, password, nxapi_port, output, temp_output):
    """ diff between original file and tmp file """
    remove_vlan = list()

    for vlan in get_nxos_info(hostname,
                              username,
                              password,
                              nxapi_port,
                              "show vlan brief")["result"]["body"]["TABLE_vlanbriefxbrief"]["ROW_vlanbriefxbrief"]:

        try:
            if vlan["vlanshowbr-vlanid"] == ("1" and "100"):
                continue
        except TypeError:
            continue

        try:
            vlan["vlanshowplist-ifidx"]
        except KeyError:
            remove_vlan.append(vlan["vlanshowbr-vlanid"])

    features_diff = set(temp_output["features"]).difference(output["features"])
    ntp_diff = set(temp_output["ntp"]).difference(output["ntp"])

    features_diff = list(features_diff)
    ntp_diff = list(ntp_diff)

    remove = dict()

    remove['features'] = features_diff
    remove["ntp"] = ntp_diff
    remove["vlans"] = remove_vlan

    return remove


def main():
    module = AnsibleModule(argument_spec=dict(
        hostname=dict(type="str", required=True),
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        nxapi_port=dict(type="str", required=True),
        src_file=dict(type="str", required=True),
        dst_file=dict(type="str", required=True)))

    output = read_nxos_config(module.params["src_file"])

    temp_output = read_nxos_tmp_config(module.params["dst_file"])

    module.exit_json(ansible_facts=differ(module.params["hostname"],
                                          module.params["username"],
                                          module.params["password"],
                                          module.params["nxapi_port"],
                                          output,
                                          temp_output))


if __name__ == "__main__":
    main()
