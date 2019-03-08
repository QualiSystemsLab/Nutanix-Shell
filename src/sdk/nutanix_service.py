import json
import requests
import uuid
from cloudshell.cp.core.models import DeployAppResult, VmDetailsData, VmDetailsProperty, VmDetailsNetworkInterface
import re


class NutanixService:

    def __init__(self, nutanix_host, nutanix_username, nutanix_password):
        requests.packages.urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.auth = (nutanix_username, nutanix_password)
        self.session.verify = False
        self.session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

        self.nutanix_base_url = 'https://' + nutanix_host + ':9440/PrismGateway/services/rest/v2.0'

    def can_connect(self):
        '''ret = False

        connect_url = self.nutanix_base_url + '/vms'
        #connect_url = 'https://10.154.3.20:9440/PrismGateway/services/rest/v2.0'

        response = self.session.get(connect_url)
        if response.status_code == 200:
            ret = True
        return ret'''
        return True

    def deploy(self, vm_name, memory, vcpu, network_uuid, requested_ip):
        '''
        deploy_vm_url = self.nutanix_base_url + '/vms'
        data = {
            "memory_mb": int(memory),
            "num_vcpus": int(vcpu),
            "name": vm_name,
            "vm_nics": [
                {
                    "network_uuid": network_uuid,
                    "request_ip": True,
                    "requested_ip_address": requested_ip
                }
            ]
        }
        json_data = json.dumps(data)
        response = self.session.post(deploy_vm_url, data=json_data)
        json_response = response.json()
        return json_response['task_uuid']
        '''

        pass

    def clone_vm(self, deploy_action):
        '''vm_unique_name = deploy_action.actionParams.appName + '__' + str(uuid.uuid4())[:6]
        source_vm_uuid = deploy_action.actionParams.deployment.attributes["Nutanixshell.Nutanix_Clone_From_VM.Cloned VM UUID"]
        storage_uuid = deploy_action.actionParams.deployment.attributes["Nutanixshell.Nutanix_Clone_From_VM.Storage Container UUID"]

        clone_vm_url = self.nutanix_base_url + '/vms/' + source_vm_uuid + '/clone'

        if source_vm_uuid == '':
            data = {"spec_list": [{"name": vm_unique_name}],
                    "uuid": source_vm_uuid
                    }
        else:
            data = {"spec_list": [{"name": vm_unique_name}],
                    "storage_container_uuid": storage_uuid,
                    "uuid": source_vm_uuid
                    }

        json_data = json.dumps(data)
        response = self.session.post(clone_vm_url, data=json_data)
        if response.status_code != 200:
            return DeployAppResult(actionId=deploy_action.actionId, success=False,
                                   errorMessage="Failed to Clone VM. Status Code: " + response.status_code)

        json_response = response.json()

        vm_uuid = self.vm_uuid_from_name(vm_unique_name)
        vm_details_data = self.extract_vm_details(vm_uuid)

        return DeployAppResult(actionId=deploy_action.actionId,
                               success=True,
                               vmUuid=vm_uuid,
                               vmName=vm_unique_name,
                               deployedAppAddress=vm_details_data.vmNetworkData[0].privateIpAddress,
                               vmDetailsData=vm_details_data)'''
        vm_name = 'TestApp__{}'.format(str(uuid.uuid4())[:6])
        vm_instance_data = [
            VmDetailsProperty(key='Instance Name', value=vm_name)
        ]
        for i in range(1):
            network_data = [
                VmDetailsProperty(key='Device Index', value=str(i)),
                VmDetailsProperty(key='MAC Address', value=str(uuid.uuid4())),
                VmDetailsProperty(key='Speed', value='1KB'),
            ]

            vm_network_data = [VmDetailsNetworkInterface(interfaceId=i, networkId=i,
                                                          isPrimary=i == 0,
                                                          # specifies whether nic is the primary interface
                                                          isPredefined=False,
                                                          # specifies whether network existed before reservation
                                                          networkData=network_data,
                                                          privateIpAddress='10.0.0.' + str(i),
                                                          publicIpAddress='8.8.8.' + str(i))]
        vm_details_data = VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data)

        return DeployAppResult(actionId=deploy_action.actionId,
                               success=True,
                               vmUuid='123456',
                               vmName=vm_name,
                               deployedAppAddress='1.2.3.4',
                               vmDetailsData=vm_details_data)

    '''def clone_vm(self, source_vm_uuid, target_storage_container_uuid, target_vm_name):
        clone_vm_url = self.nutanix_base_url + '/vms/' + source_vm_uuid + '/clone'
        data = {"spec_list": [{"name": target_vm_name}],
                "storage_container_uuid": target_storage_container_uuid,
                "uuid": source_vm_uuid
                }
        json_data = json.dumps(data)
        response = self.session.post(clone_vm_url, data=json_data)
        json_response = response.json()
        return json_response['task_uuid']
    '''

    def delete_vm(self, vm_uuid):
        '''delete_vm_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/?delete_snapshots=true'
        response = self.session.delete(delete_vm_url)
        json_response = response.json()
        return json_response['task_uuid']'''
        pass

    def set_power_on(self, vm_uuid):
        '''set_power_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/set_power_state/'
        data = {"transition": "ON",
                "uuid": vm_uuid
                }
        json_data = json.dumps(data)
        response = self.session.post(set_power_url, data=json_data)
        json_response = response.json()
        return json_response['task_uuid']'''
        pass

    def set_power_off(self, vm_uuid):
        '''set_power_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/set_power_state/'
        data = {"transition": "OFF",
                "uuid": vm_uuid
                }
        json_data = json.dumps(data)
        response = self.session.post(set_power_url, data=json_data)
        json_response = response.json()
        return json_response['task_uuid']'''
        pass

    def extract_vm_details(self, vm_uuid):
        vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uuid + '?include_vm_nic_config=true'
        response = self.session.get(vm_detail_url)
        json_response = response.json()

        vm_name = json_response['name']

        vm_instance_data = [
            VmDetailsProperty(key='Instance Name', value=json_response['name'])
        ]
        vm_network_data = []

        i = 0
        for nic in json_response['vm_nics']:
            network_data = [
                VmDetailsProperty(key='MAC Address', value=nic['mac_address']),
            ]

            current_interface = VmDetailsNetworkInterface(interfaceId=i,
                                                          networkId=nic['network_uuid'],
                                                          isPredefined=True,
                                                          networkData=network_data,
                                                          privateIpAddress=nic['ip_address'])
            i += 1
            vm_network_data.append(current_interface)

        return VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data)

    def get_vm_details(self, vm_name, vm_uuid):

        '''vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uuid + '?include_vm_nic_config=true'
        response = self.session.get(vm_detail_url)
        json_response = response.json()

        vm_name = json_response['name']

        vm_instance_data = [
            VmDetailsProperty(key='Instance Name', value=json_response['name'])
        ]
        vm_network_data = []
        i = 0

        for nic in json_response['vm_nics']:
            network_data = [
                VmDetailsProperty(key='MAC Address', value=nic['mac_address']),
            ]

            current_interface = VmDetailsNetworkInterface(interfaceId=i,
                                                          networkId=nic['network_uuid'],
                                                          isPrimary=i == 0,
                                                          isPredefined=True,
                                                          networkData=network_data,
                                                          privateIpAddress=nic['ip_address'])
            vm_network_data.append(current_interface)
            i += 1

        return VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data, appName=vm_name)'''

        vm_instance_data = [
            VmDetailsProperty(key='Instance Name', value=vm_name)
        ]

        network_data = [
            VmDetailsProperty(key='Device Index', value=str(0)),
            VmDetailsProperty(key='MAC Address', value=str(uuid.uuid4())),
            VmDetailsProperty(key='Speed', value='1KB'),
        ]

        vm_network_data = [VmDetailsNetworkInterface(interfaceId=0, networkId=0,
                                                      isPrimary=True,
                                                      # specifies whether nic is the primary interface
                                                      isPredefined=False,
                                                      # specifies whether network existed before reservation
                                                      networkData=network_data,
                                                      privateIpAddress='10.0.0.' + str(0),
                                                      publicIpAddress='8.8.8.' + str(0))]

        return VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data, appName=vm_name)


    def refresh_ip(self, cloudshell_session, app_fullname, vm_uid, app_private_ip, app_public_ip, ip_regex, timeout):
        INTERVAL = 5
        IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

        time_elapsed = 0
        ip_regex = re.compile(ip_regex).match
        ip = None




        '''vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uid + '?include_vm_nic_config=true'
        response = self.session.get(vm_detail_url)
        json_response = response.json()

        queried_private_ip = json_response['vm_nics'][0]['ip_address']
        queried_public_ip = None

        if app_private_ip != queried_private_ip:
            cloudshell_session.UpdateResourceAddress(app_fullname, queried_private_ip)

        if not app_public_ip or app_public_ip != queried_public_ip:
            cloudshell_session.UpdateResourceAddress(app_fullname, "Public IP", queried_public_ip)'''

        if app_private_ip != '1.2.3.4':
            cloudshell_session.UpdateResourceAddress(app_fullname, '1.2.3.4')

    def vm_uuid_from_name(self, vm_name):
        list_of_vms = self.list_vms()

        for each in list_of_vms:
            if each['name'] == vm_name:
                return each['uuid']
        raise StandardError("VM: " + vm_name + " not found")

    def list_vms(self):
        vm_url = self.nutanix_base_url + '/vms'
        response = self.session.get(vm_url)
        json_response = response.json()
        return json_response['entities']

    #######################################################
    # Below are not needed for the default cloud provider #
    #######################################################

    def locate_vm_uuid(self, vm_json_output, vm_name):
        for each in vm_json_output:
            if each['name'] == vm_name:
                return each['uuid']
        return 1

    def get_vm_nic(self, vm_uuid):
        vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/nics/?include_address_assignments=true'
        response = self.session.get(vm_detail_url)
        json_response = response.json()
        return json_response['entities']

    def get_storage_container(self):
        storage_container_list = []
        storage_container_url = self.nutanix_base_url + '/storage_containers/'
        response = self.session.get(storage_container_url)
        json_response = response.json()
        for each in json_response['entities']:
            storage_container_list.append(each['name'] + ',' + each['storage_container_uuid'])
        return storage_container_list

    def get_image_list(self):
        image_list_url = self.nutanix_base_url + '/images/'
        response = self.session.get(image_list_url)
        json_response = response.json()
        return json_response['entities']

    def list_vm_snapshot(self, vm_uuid):
        vm_snapshot_list = []
        vm_snapshot_list_url = self.nutanix_base_url + '/snapshots/?vm_uuid=' + vm_uuid
        response = self.session.get(vm_snapshot_list_url)
        json_response = response.json()
        for each in json_response['entities']:
            vm_snapshot_list.append(each['snapshot_name'] + ',' + each['uuid'])
        return vm_snapshot_list

    def restore_vm_snapshot(self, snapshot_uuid, vm_uuid):
        restore_vm_snapshot_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/restore'
        data = {
                "restore_network_configuration": "true",
                "snapshot_uuid": snapshot_uuid,
                "uuid": vm_uuid
                }
        json_data = json.dumps(data)
        response = self.session.post(restore_vm_snapshot_url, data=json_data)
        json_response = response.json()
        return json_response['task_uuid']

    def delete_vm_snapshot(self, snapshot_uuid):
        delete_vm_snapshot_url = self.nutanix_base_url + '/snapshots/' + snapshot_uuid
        response = self.session.delete(delete_vm_snapshot_url)
        json_response = response.json()
        return json_response['task_uuid']

    def create_vm_snapshot(self, snapshot_name, vm_uuid):
        create_vm_snapshot_url = self.nutanix_base_url + '/snapshots/'
        data = {
                "snapshot_specs": [
                        {
                            "snapshot_name": snapshot_name,
                            "vm_uuid": vm_uuid
                        }
                    ]
                }
        json_data = json.dumps(data)
        response = self.session.post(create_vm_snapshot_url, data=json_data)
        json_response = response.json()
        return json_response['task_uuid']

    def task_status(self, job_id):
        task_status_url = self.nutanix_base_url + '/tasks/' + job_id
        response = self.session.get(task_status_url)
        json_response = response.json()
        return json_response['progress_status']
