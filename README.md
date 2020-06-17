# webinar

#### webinar_part_1

In webinar part 1 we showed three different usecases.

1) Ansible  
    Prerequisites:
    * Ansible installed on local machine
    * Cisco ACI
    * One or more target machines

    How-to-use:
    * `pip3 install -r requirements.txt` to install dependencies
    * `python3 setup_aci.py` with variables to create group_vars and hosts file with all needed information.
    * `python3 setup_server.py` with variables to create group_vars and hosts files with all needed information.
    * `ansible-playbook aci.yml -i hosts` to run the playbook towards Cisco ACI.
    * `ansible-playbook server.yml -i hosts` to run the playbook towards target machines.
    
    What the playbooks will perform:  
    aci.yml   
    * Create Tenant
    * Create VRF
    * Create Bridge Domain
    * Create Subnet on Bridge Domain
    * Create Application Profile
    * Create Endpoint Group(s)
    * Create Contract(s), Subject(s), Filter(s)
    * Create Contract(s) to EPG binding(s)
    
    server.yml
    * apt-update
    * Install apache2
    * Remove old index.html
    * Copy new index.html from roles/webserver/files to target machines

2) Terraform  
    Prerequisites:
    * Terraform installed on local machine
    * Cisco ACI
    * VMware
    * VMware template (Ubuntu, called ubuntu_template)
    * Cisco ACI to VMware VMM integration
    
    How-to-use:
    * `python3 setup_tf.py` with variables to create terraform.tfvars file with all needed information.
    * Make changes to aci.tf and vmware.tf to your choosing (or use examples).
    * `terraform init`
    * `terraform plan`
    * `terraform apply` and answer `yes`
    * (OPTIONAL) `terraform destroy` and answer `yes`
    
    What Terraform will perform:  
    * Create Tenant
    * Create VRF
    * Create Bridge Domains
    * Create Subnet on Bridge Domains
    * Create Application Profile
    * Create Endpoint Groups
    * Create Contracts, Subjects, Filters
    * Create Contracts to EPG bindings
    * Clone ubuntu_template and spin up two VMs

3) Infrastructure-as-code using Ansible, Terraform and Gitlab CI/CD  
    Prerequisites:
    * Self-hosted Gitlab
    * Cisco ACI
    * VMware
    * VMware template (Ubuntu, called ubuntu_template)
    * Cisco ACI to VMware VMM integration
    
    How-to-use:
    * `pip3 install -r requirements.txt` to install dependencies
    * `python3 setup_iac.py` with variables to create terraform.tfvars file with all needed information.
    * Make changes to aci.tf and vmware.tf to your choosing (or use examples)
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

    This will now start a CI/CD Pipeline in Gitlab and when it's done you will be able to access \<web> ip and test the Database connection. 
    
    What IAC will perform:
    * Create Tenant
    * Create VRF
    * Create Bridge Domains
    * Create Subnet on Bridge Domains
    * Create Application Profile
    * Create Endpoint Groups
    * Create Contracts, Subjects, Filters
    * Create Contracts to EPG bindings
    * Clone template and spin up two VMs (web and db)
    * Run two ansible-playbooks
        - web: will install apache2 and copy demo website
        - db: will install mariadb and inject demo data

#### webinar_part_2

In webinar part 2 we showed two different usecases.

1) NXOS with ansible and Gitlab CD/CD
    Prerequisites:
    * Ansible installed on local machine
    * Cisco Nexus (VM or Hardware)
    * Self-hosted Gitlab
    
    How-to-use:
    * `pip3 install -r requirements.txt` to install dependencies
    * `python3 setup.py` with variables to create group_vars/all, group_vars/vault and hosts with all needed information.
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
    
2) NXOS with Ansible, Netbox and Gitlab CI/CD
    Prerequisites:
    * Ansible installed on local machine
    * Cisco Nexus (VM or Hardware)
    * Self-hosted Gitlab
    * Self-hosted Netbox
    
    How-to-use:
    * `pip3 install -r requirements.txt` to install dependencies
    * Create a project in gitlab
        * CI/CD variables needed:
            - `ANSIBLE_VAULT_PASSWORD` 
        * Create a pipeline trigger
    * `python3 setup.py` with variables to create group_vars/all, group_vars/vault and hosts with all needed information.
    * Copy `netbox_tools/webhook_proxy_svc.py` to Netbox
    * SSH to Netbox and run
        - `apt install screen`
        - `screen`
        - `gunicorn -b :5000 --access-logfile - --error-logfile - webhook_proxy_svc:app`
        - `ctrl + a + d`
        - `exit`
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
