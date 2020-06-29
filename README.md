# Automation webinar (cisco aci, nxos, vmware with more)

#### webinar_part_1

video: https://www.miradot.se/news/webinar-om-automation-del-1/

# Ansible  
## Prerequisites
* Ansible installed on local machine
* Cisco ACI
* One or more target machines

## Use Case Description
aci.yml   
* Creates ACI Tenant
* Creates ACI VRF
* Creates ACI Bridge Domain
* Creates ACI Subnet on Bridge Domain
* Creates ACI Application Profile
* Creates ACI Endpoint Group(s)
* Creates ACI Contract(s), Subject(s), Filter(s)
* Creates ACI Contract(s) to EPG binding(s)

server.yml
* Runs apt-update
* Installs apache2
* Removes old index.html
* Copies new index.html from roles/webserver/files to target machine(s)

## Installation
These installation instructions assumes you have a python environment with python-pip installed.
```
pip3 install -r requirements.txt
```

## Usage
```
(OPTION 1) python3 setup_aci.py 
(OPTION 2) python3 setup_server.py
(OPTION 1) ansible-playbook aci.yml -i hosts 
(OPTION 2) ansible-playbook server.yml -i hosts
``` 
   
# Terraform
## Prerequisites
* Terraform installed on local machine
* Cisco ACI
* VMware
* VMware template (Ubuntu, called ubuntu_template)
* Cisco ACI to VMware VMM integration
  
## Use Case Description
* Creates ACI Tenant
* Creates ACI VRF
* Creates ACI Bridge Domains
* Creates ACI Subnet on Bridge Domains
* Creates ACI Application Profile
* Creates ACI Endpoint Groups
* Creates ACI Contracts, Subjects, Filters
* Creates ACI Contracts to EPG bindings
* Clones VMware ubuntu_template and spins up two VMs

## Installation

## Usage
```
python3 setup_tf.py
Make changes to aci.tf and vmware.tf to your choosing (or use examples).
terraform init
terraform plan
terraform apply ; yes
(OPTIONAL) terraform destroy ; yes
``` 

# Infrastructure-as-code using Ansible, Terraform and Gitlab CI/CD  
## Prerequisites
* Self-hosted Gitlab
* Cisco ACI
* VMware
* VMware template (Ubuntu, called ubuntu_template)
* Cisco ACI to VMware VMM integration

## Use Case Description
* Creates ACI Tenant
* Creates ACI VRF
* Creates ACI Bridge Domains
* Creates ACI Subnet on Bridge Domains
* Creates ACI Application Profile
* Creates ACI Endpoint Groups
* Creates ACI Contracts, Subjects, Filters
* Creates ACI Contracts to EPG bindings
* Clones VMware template and spins up two VMs (web and db)
* Runs two ansible-playbooks
    - web: will install apache2 and copy demo website
    - db: will install mariadb and inject demo data

## Installation
These installation instructions assumes you have a python environment with python-pip installed.
```
pip3 install -r requirements.txt
```

## Usage
* `python3 setup_iac.py`
* Make changes to aci.tf and vmware.tf to your choosing (or use examples).
* Create a project in gitlab
    * CI/CD variables needed:
        * `ANSIBLE_VAULT_PASSWORD` ; Password chosen in setup_iac.py (-pv) 
        * `CI_PUSH_TOKEN` ; User settings > Access Tokens > Choose a Name and check "write_repository"
        * `CI_PUSH_USER`
        * `CI_PUSH_URL` ; gitlab.lab.local
        * `CI_PROJECT_NAME`
        * `TF_ACI_PASS` ; ACI Password
        * `TF_OSHIFT_TOKEN` ; Openshift Token (if not existing just add "asd" as Value)
        * `TF_VC_PASS` ; vCenter Password
* Clone down your newly created project : `git clone <url>`
* Copy content of 3.0_iac folder to your project : `cp -r 3.0_iac/ <folder in step above>`
* Enter your project : `cd <folder in step above>`
* `git add .`
* `git commit -m "my awesome iac"`
* `git push`
* If you get the following error `remote: You are not allowed to push code to this project.` Run the following (substitute for your environment) `git remote set-url origin http://<username>:<cipushtoken>@$<fqdntogitlab>/<username>/<projectname>.git`
* `git push`

#### webinar_part_2

video: https://www.miradot.se/news/webinar-om-automation-del-2/

# NXOS with ansible and Gitlab CD/CD
## Prerequisites:
* Ansible installed on local machine
* Cisco Nexus (VM or Hardware)
* Self-hosted Gitlab

## Use Case Description
Will gather information from specified NXOS devices and parse the configuration. After the configuration and files 
has been pushed to gitlab it's possible to manage the device(s) with git.

## Installation
These installation instructions assumes you have a python environment with python-pip installed.
```
pip3 install -r requirements.txt
```

## Usage    
* `python3 setup.py`
* Create a project in gitlab
    * CI/CD variables needed:
        * `ANSIBLE_VAULT_PASSWORD` ; Password chosen in setup_iac.py (-pv) 
* Clone down your newly created project : `git clone <url>`
* Copy content of 1.0_nxos_existing_no_netbox folder to your project : `cp -r 1.0_nxos_existing_no_netbox/ <folder in step above>`
* Enter ansible folder in your project : `cd <folder in step above>/ansible`
* `ansible-playbook init.yml -i hosts --ask-vault-pass`
* `cd ..`
* `git add .`
* `git commit -m "[skip ci] new host_vars"`
* `git push`
* If you get the following error `remote: You are not allowed to push code to this project.` Run the following (substitute for your environment) `git remote set-url origin http://<username>:<cipushtoken>@$<fqdntogitlab>/<username>/<projectname>.git`
* `git push`
* Make changes to the ansible/host_vars files according to preferences
* `git add .`
* `git commit -m "changes"`
* `git push`
    
# NXOS with Ansible, Netbox and Gitlab CI/CD
## Prerequisites:
* Ansible installed on local machine
* Cisco Nexus (VM or Hardware)
* Self-hosted Gitlab
* Self-hosted Netbox

## Use Case Description
Will gather information from specified NXOS devices and parse the configuration. After the configuration and files 
has been pushed to gitlab it's possible to manage the device(s) with git and Netbox.

## Installation
these installation instructions assumes you have a python environment with python-pip installed.
```
pip3 install -r requirements.txt
```

## Usage
* Create a project in gitlab
    * CI/CD variables needed:
        - `ANSIBLE_VAULT_PASSWORD` 
    * Create a pipeline trigger
* `python3 setup.py` with variables to create group_vars/all, group_vars/vault and hosts with all needed information.
* Copy `netbox_tools/webhook_proxy_svc.py` to Netbox
* SSH to Netbox and run
    ```
    apt install screen
    screen
    gunicorn -b :5000 --access-logfile - --error-logfile - webhook_proxy_svc:app
    ctrl + a + d
    exit
    ```
* Goto Netbox: `http://\<fqdn>/admin/extras/webhook/`
    - Name: `interfaces_update`
    - Object types:` dcim > interface`
    - `Enabled checked`
    - `Type create checked`
    - `Type update checked`
    - URL: `http://localhost:5000/netbox_webhook/`
    - HTTP method: `POST`
    - HTTP content type: `application/json`
    - Body template: `{"msg": "interfaces updated"}`     
* Clone down your newly created project : `git clone <url>`
* Copy content of 2.0_nxos_existing_with_netbox folder to your project : `cp -r 2.0_nxos_existing_with_netbox/ <folder in step above>`
* Enter ansible folder in your project : `cd <folder in step above>/ansible`
* `ansible-playbook init.yml -i hosts --ask-vault-pass`
* `cd ..`
* `git add .`
* `git commit -m "[skip ci] new host_vars"`
* `git push`
* If you get the following error `remote: You are not allowed to push code to this project.` Run the following (substitute for your environment) `git remote set-url origin http://<username>:<cipushtoken>@$<fqdntogitlab>/<username>/<projectname>.git`
* `git push`
* Make changes to the ansible/host_vars files according to preferences
* `git add .`
* `git commit -m "changes"`
* `git push`
* OR
* Make Name/Interface changes in Netbox according to preferences
    - Support:
        * Name change
        * Description change
        * Access vlan change
* Make description/access vlan changes with sommerjobber tool: `cd netbox_tools` `python3 tool.py`

## Getting help

If you have questions, concerns, bug reports, etc., please create an issue against this repository.

## Getting involved

This project is supposed to work as a tutorial on how to get started with Intersight. If you have any suggestions on what else to include, feel free to reach ut by creating an issue.

## Licensing info

`Copyright (c) 2020, Miradot AB`

This code is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

