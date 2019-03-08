import json
import requests
import uuid
import time
import re
from cloudshell.cp.core.models import DeployAppResult, VmDetailsData, VmDetailsProperty, VmDetailsNetworkInterface


class NutanixService:

    def __init__(self, nutanix_host, nutanix_username, nutanix_password):
        requests.packages.urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.auth = (nutanix_username, nutanix_password)
        self.session.verify = False
        self.session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

        self.nutanix_base_url = 'https://' + nutanix_host + ':9440/PrismGateway/services/rest/v2.0'

    def can_connect(self, storage_uuid):
        ret = False

        connect_url = self.nutanix_base_url + '/vms'

        response = self.session.get(connect_url)
        if response.status_code == 200 or response.status_code == 201:
            ret = self.is_valid_storage(storage_uuid)

        return ret

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

    def clone_vm(self, deploy_action, storage_uuid):
        vm_unique_name = deploy_action.actionParams.appName + '__' + str(uuid.uuid4())[:6]
        source_vm_uuid = deploy_action.actionParams.deployment.attributes["Nutanixshell.Nutanix_Clone_From_VM.Cloned VM UUID"]

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
        if response.status_code != 200 and response.status_code != 201:
            return DeployAppResult(actionId=deploy_action.actionId, success=False,
                                   errorMessage="Failed to Clone VM. Status Code: {}, {}, {}, {}".format(str(response.status_code),
                                                                                                         vm_unique_name,
                                                                                                         source_vm_uuid,
                                                                                                         storage_uuid))

        json_response = response.json()
        task_uuid = json_response['task_uuid']
        check_task_url = self.nutanix_base_url + '/tasks/' + task_uuid

        task_in_progress = True

        while task_in_progress:
            time.sleep(1)

            response = self.session.get(check_task_url)
            json_response = response.json()
            if json_response['progress_status'] == 'Succeeded':
                task_in_progress = False
            elif json_response['progress_status'] == 'Failed':
                return DeployAppResult(actionId=deploy_action.actionId, success=False,
                                       errorMessage="Nutanix failed to Clone VM, check Nutanix task logs")

        vm_uuid = self.vm_uuid_from_name(vm_unique_name)

        vm_details_data = self.extract_vm_details(vm_uuid)

        return DeployAppResult(actionId=deploy_action.actionId,
                               success=True,
                               vmUuid=vm_uuid,
                               vmName=vm_unique_name,
                               deployedAppAddress=vm_details_data.vmNetworkData[0].privateIpAddress,
                               vmDetailsData=vm_details_data)

    def delete_vm(self, vm_uuid):
        delete_vm_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/?delete_snapshots=true'
        response = self.session.delete(delete_vm_url)

        if response.status_code != 200 and response.status_code != 201:
            raise StandardError("Unable to delete VM. uid: {}".format(vm_uuid))

        json_response = response.json()
        return json_response['task_uuid']

    def set_power_on(self, vm_uuid):
        set_power_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/set_power_state/'
        data = {"transition": "ON",
                "uuid": vm_uuid
                }
        json_data = json.dumps(data)
        response = self.session.post(set_power_url, data=json_data)

        if response.status_code != 200 and response.status_code != 201:
            raise StandardError("Unable to power on VM. uid: {}".format(vm_uuid))

        json_response = response.json()
        return json_response['task_uuid']

    def set_power_off(self, vm_uuid):
        set_power_url = self.nutanix_base_url + '/vms/' + vm_uuid + '/set_power_state/'
        data = {"transition": "OFF",
                "uuid": vm_uuid
                }
        json_data = json.dumps(data)
        response = self.session.post(set_power_url, data=json_data)

        if response.status_code != 200 and response.status_code != 201:
            raise StandardError("Unable to power off VM. uid: {}".format(vm_uuid))

        json_response = response.json()
        return json_response['task_uuid']

    def extract_vm_details(self, vm_uuid):
        '''vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uuid + '?include_vm_nic_config=true'
        in_progress = True

        while in_progress:
            response = self.session.get(vm_detail_url)
            if response.status_code != 200:
                raise StandardError("Unable to extract VM details. uid: {}".format(vm_uuid))
            json_response = response.json()
            if 'vm_nics' in json_response and json_response['vm_nics'] != [] and 'ip_address' in json_response['vm_nics']:
                in_progress = False
            else:
                time.sleep(5)'''

        vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uuid + '?include_vm_nic_config=true'
        response = self.session.get(vm_detail_url)

        if response.status_code != 200 and response.status_code != 201:
            raise StandardError("Unable to extract VM details. uid: {}".format(vm_uuid))

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
                                                          networkData=network_data)
            i += 1
            vm_network_data.append(current_interface)

        return VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data)

    def get_vm_details(self, vm_name, vm_uuid):

        vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uuid + '?include_vm_nic_config=true'
        response = self.session.get(vm_detail_url)

        if response.status_code != 200 and response.status_code != 201:
            raise StandardError("Unable to get VM details. uid: {}".format(vm_uuid))

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

        return VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data, appName=vm_name)

    def refresh_ip(self, cloudshell_session, app_fullname, vm_uid, app_private_ip, app_public_ip, ip_regex, timeout):
        INTERVAL = 5
        IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
        vm_detail_url = self.nutanix_base_url + '/vms/' + vm_uid + '?include_vm_nic_config=true'

        time_elapsed = 0
        is_ip_match = re.compile(ip_regex).match
        ip = None
        temp_ip = None

        while time_elapsed < timeout and not ip:
            response = self.session.get(vm_detail_url)
            if response.status_code != 200 and response.status_code != 201:
                raise StandardError("Unable to query for IP. uid: {}".format(vm_uid))
            json_response = response.json()

            if 'vm_nics' in json_response and json_response['vm_nics'] != [] and 'ip_address' in json_response['vm_nics'][0]:
                temp_ip = json_response['vm_nics'][0]['ip_address']

            if temp_ip:
                if IP_V4_PATTERN.match(temp_ip) and is_ip_match(temp_ip):
                    ip = temp_ip

            if not ip:
                time_elapsed += INTERVAL
                time.sleep(INTERVAL)

        if not ip:
            raise ValueError('IP address of VM \'{0}\' could not be obtained during {1} seconds'
                             .format(app_fullname, timeout))

        if app_private_ip != ip:
            cloudshell_session.UpdateResourceAddress(app_fullname, ip)

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

    def is_valid_storage(self, storage_uuid):
        ret = False
        storage_container_url = self.nutanix_base_url + '/storage_containers/'
        response = self.session.get(storage_container_url)

        if response.status_code != 200 and response.status_code != 201:
            raise StandardError("Unable to Verify Storage Container UUID. uid: {}".format(storage_uuid))

        json_response = response.json()
        for each in json_response['entities']:
            if each['storage_container_uuid'] == storage_uuid:
                ret = True
                break
        return ret

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
