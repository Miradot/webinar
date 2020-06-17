from dialog import Dialog
from collections import OrderedDict
from inventory import get_conn, get_site_list, get_devices, get_interfaces, get_vlans
import time

class DropChangesError(Exception):
    pass

def prompt_user_with_prefilled_form(d, title, elements):
    '''
    This method presents the user with a dialog based input form with its current values
    all the field values are then returned regardless if they were updated or not

    Args:
        ucs_conn (UcsHandle): the ucs connection
        d (Dialog): dialoge object used to present the user with a message
        title (string): A text describing what the user needs to do
        elements (list): A list holding tuples with each entries (name, and existing value)
    Returns:
        A list of the values returned from the form, inte the same order as they were supplied
    '''

    # construct the form data with the parameters needed by dialog
    form_elements = list()
    row_counter = 2
    for this_element in elements:
        entry = (
            this_element[0], # field name
            row_counter,
            3, # static form config data
            this_element[1], # field value
            row_counter,
            25, # static form config data
            20, # static form config data
            0 # static form config data
        )
        form_elements.append(entry)
        row_counter += 1

    # now present the user with a dialog window based on our prepared list of options
    code, form_data = d.form(title, form_elements, height=20, width=60, form_height=10)

    # return the form or let the user leave the program
    if code == 'ok':
        return form_data
    else:
        raise DropChangesError

def prompt_user_with_list_of_options(d, title, list_of_options, width=None, height=None):
    '''
    This method presents the user with a dialog based list of options
    '''
    option_map = OrderedDict()
    option_list = list()
    key_id = 1

    # 
    for entry in list_of_options:
        option_map[str(key_id)] = entry
        option_list.append((str(key_id), str(entry)))
        key_id += 1

    # now present the user with a dialog window based on our prepared list of options
    code, tag = d.menu(title, height=height, width=width, menu_height=None, choices=option_list)

    # return the form or let the user leave the program
    if code == 'ok':
        return option_map[tag]
    else:
        raise DropChangesError

def prompt_user_with_an_info_box(d, text, width=None, height=None):
    d.infobox(text, height=height, width=width)
    time.sleep(2)

def prompt_user_with_an_entry_box(d, text, current_value, width=None, height=None):
    code, tag = d.inputbox(text, height=height, width=width, init=current_value)
    if code == 'ok':
        return tag
    else:
        raise DropChangesError

def modify_interface_dialog(d, vlan_objs, interface_obj):
    # first, prompt our user they are on the right interface
    msg_line = 'Entering configuration dialog for interface:\n    - {}'.format(interface_obj.name)
    prompt_user_with_an_info_box(d, msg_line, 50, 4)

    # second, check if the user is happy with the current descr
    interface_obj.description = prompt_user_with_an_entry_box(d, 'Set a description', interface_obj.description)

    # last, let the user chose between the vlans available
    interface_obj.untagged_vlan = prompt_user_with_list_of_options(d, 'Choose a VLAN', vlan_objs, 50)
    interface_obj.mode = 100 # id 100 is "Access"

def get_interface_lldp_neighbor(device, interface):
    from napalm import get_network_driver
    optional_args = {'port': '5001', 'nxos_protocol': 'http'}
    nxos_driver = get_network_driver('nxos')
    nxos = nxos_driver(hostname=device, username='admin', password='miradot1', optional_args=optional_args)
    nxos.open()

    resultat = nxos.get_lldp_neighbors()

    if interface in resultat.keys():
        return ['{} - {}'.format(x['hostname'], x['port']) for x in resultat[interface]]

    return []


def main():
    d = Dialog(dialog="dialog", autowidgetsize=True)
    d.set_background_title("Sommarjobber-tool")

    nb = get_conn()

    # first get a list of sites and let the user choose one
    sites = get_site_list(nb)
    site_map = {str(x):x for x in sites}
    site_chosen_key = prompt_user_with_list_of_options(d, 'please choose a site', site_map.keys())

    # get a list of vlans available to the chosen site
    vlan_objs = get_vlans(nb, site_chosen_key)

    # now get a list of devices in this site and let the user choose one
    devices = get_devices(nb, site_chosen_key)
    device_map = {str(x):x for x in devices}
    device_chosen_key = prompt_user_with_list_of_options(d, 'please choose a device', device_map.keys())

    # get a list of interface for the chosen device and site and let the user choose one

    interface_map = OrderedDict()
    interfaces = get_interfaces(nb, device_chosen_key, site_chosen_key)

    for this_interface in interfaces:
        interface_map[str(this_interface)] = this_interface

    interface_chosen_key = prompt_user_with_list_of_options(d, 'please choose an interface', interface_map.keys())
    interface_obj = interface_map[interface_chosen_key]

    try:
        # we've now found an interface to work with - offer the user the options available
        tag = prompt_user_with_list_of_options(d, 'what do you want to do?', ['configure', 'check'])

        if tag == 'configure':
            # present the user with a modification dialog
            modify_interface_dialog(d, vlan_objs, interface_obj)
            interface_obj.save()
            prompt_user_with_an_info_box(d, 'Changes were comitted - executing deployment', 70, 5)
        elif tag == 'check':
            prompt_user_with_an_info_box(d, 'Polling status of interface {} of device {}'.format(interface_chosen_key, device_chosen_key), 70, 5)            
            text = 'Interface known lldp-neighbors:\n    -'
            text += '\n    -'.join(get_interface_lldp_neighbor(device_chosen_key, interface_chosen_key))
            prompt_user_with_an_info_box(d, text, 70, 5)
    except DropChangesError:
        prompt_user_with_an_info_box(d, 'The user aborted the tool - returning to main menu', 70, 5)
        pass

    main()




if __name__ == '__main__':
    main()