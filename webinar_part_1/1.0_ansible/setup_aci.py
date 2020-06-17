import yaml
import argparse
import sys


def create_file(args):

    config = dict()

    config["TENANT_NAME"] = args.tenant
    config["AP_NAME"] = args.app
    config["VRF_NAME"] = args.vrf
    config["BD_NAME"] = args.bd
    config["BD_GATEWAY"] = args.subnet.split("/")[0]
    config["BD_GATEWAY_MASK"] = int(args.subnet.split("/")[1])
    config["EPGS"] = args.epg
    config["CONTRACTS"] = list()
    config["CONTRACT_BINDINGS"] = list()

    for rule in args.rules:
        contract = dict()
        contract["contract"] = rule.split(",")[0]
        contract["filter"] = rule.split(",")[1]
        contract["port"] = rule.split(",")[2]
        config["CONTRACTS"].append(contract)

    for binding in args.bindings:
        contract_binding = dict()
        contract_binding["epg"] = binding.split(",")[0]
        contract_binding["contract"] = binding.split(",")[1]
        contract_binding["contract_type"] = binding.split(",")[2]
        config["CONTRACT_BINDINGS"].append(contract_binding)

    with open("group_vars/apic", "w") as file:
        yaml.dump(config, file)

    with open("hosts", "w") as file:
        file.write("[apic]\n")
        file.write(args.apic + "\n")


def main():
    # show arguments for the user
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")

    required.add_argument("-t", dest="tenant", help="Tenant Name", required=True)
    required.add_argument("-v", dest="vrf", help="VRF Name", required=True)
    required.add_argument("-a", dest="app", help="Application Profile Name", required=True)
    required.add_argument("-b", dest="bd", help="Bridge Domain Name", required=True)
    required.add_argument("-s", dest="subnet", help="GatewayIP/CIDR ; 1.1.1.1/24", required=True)
    required.add_argument("-e", dest="epg", help="Endpoint Group Name ; epg1 epg2 ...", required=True, nargs='+')
    required.add_argument("-r", dest="rules", help="ContractName,FilterName,Port ; web,http,80 db,sql,1433 ...",
                          required=True, nargs='+')
    required.add_argument("-bi", dest="bindings",
                          help="EpgName,ContractName,Consumer/Provider ; epg1,web,consumer epg2,web,provider ...",
                          required=True, nargs='+')
    required.add_argument("-cn", dest="apic", help="ACI Controller IP ; 192.168.1.1", required=True)

    args = parser.parse_args()

    # if args.rules is not correct, exit out
    for line in args.rules:
        if not len(line.split(",")) % 3 == 0:
            print("rules requires contract,filter,port")
            sys.exit()

    # if bindings is not correct, exit out
    for line in args.bindings:
        if not len(line.split(",")) % 3 == 0:
            print("bindings requires epg,contract,[consumer/provider]")
            sys.exit()

    create_file(args)


if __name__ == '__main__':
    main()
