from cloudshell.cp.core import DriverRequestParser
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cp.core.utils import single, first_or_default
from cloudshell.shell.core.driver_context import InitCommandContext, AutoLoadCommandContext, ResourceCommandContext, \
    AutoLoadDetails, CancellationContext, ResourceRemoteCommandContext
from cloudshell.cp.core.models import DriverResponse, DeployApp
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from data_model import *
from sdk.nutanix_service import *


class NutanixshellDriver(ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.request_parser = DriverRequestParser()

    def initialize(self, context):
        """
        Initialize the driver session, this function is called every time a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """

        # run 'shellfoundry generate' in order to create classes that represent your data model

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'get_inventory_context_json', context)

                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                if not nutanix_service.can_connect(cloud_provider_resource.storage_container_name):
                    raise ValueError('Could not connect: Check address and verify credentials')

        return cloud_provider_resource.create_autoload_details()

    # </editor-fold>

    # <editor-fold desc="Mandatory Commands">

    def Deploy(self, context, request=None, cancellation_context=None):
        """
        Deploy
        :param ResourceCommandContext context:
        :param str request: A JSON string with the list of requested deployment actions
        :param CancellationContext cancellation_context:
        :return:
        :rtype: str
        """

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'deploy_request', request)
                self._log(logger, 'deploy_context', context)

                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                # parse the json strings into action objects
                actions = self.request_parser.convert_driver_request_to_actions(request)

                # extract DeployApp action
                deploy_action = single(actions, lambda x: isinstance(x, DeployApp))

                # if we have multiple supported deployment options use the 'deploymentPath' property
                # to decide which deployment option to use.
                # deployment_name = deploy_action.actionParams.deployment.deploymentPath

                deploy_result = nutanix_service.clone_vm(deploy_action, cloud_provider_resource.storage_container_name)

                self._log(logger, 'deploy_result', deploy_result)

                return DriverResponse([deploy_result]).to_driver_response_json()

    def PowerOn(self, context, ports):
        """
        Will power on the compute resource
        :param ResourceRemoteCommandContext context:
        :param ports:
        """

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'power_on_context', context)
                self._log(logger, 'power_on_ports', ports)
                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                resource_ep = context.remote_endpoints[0]
                deployed_app_dict = json.loads(resource_ep.app_context.deployed_app_json)
                vm_uid = deployed_app_dict['vmdetails']['uid']
                nutanix_service.set_power_on(vm_uid)

    def PowerOff(self, context, ports):
        """
        Will power off the compute resource
        :param ResourceRemoteCommandContext context:
        :param ports:
        """

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'power_off_context', context)
                self._log(logger, 'power_off_ports', ports)
                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                resource_ep = context.remote_endpoints[0]
                deployed_app_dict = json.loads(resource_ep.app_context.deployed_app_json)
                vm_uid = deployed_app_dict['vmdetails']['uid']
                nutanix_service.set_power_off(vm_uid)

    def PowerCycle(self, context, ports, delay):
        pass

    def DeleteInstance(self, context, ports):
        """
        Will delete the compute resource
        :param ResourceRemoteCommandContext context:
        :param ports:
        """
        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'DeleteInstance_context', context)
                self._log(logger, 'DeleteInstance_ports', ports)
                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                resource_ep = context.remote_endpoints[0]
                deployed_app_dict = json.loads(resource_ep.app_context.deployed_app_json)
                vm_uid = deployed_app_dict['vmdetails']['uid']
                nutanix_service.delete_vm(vm_uid)

    def GetVmDetails(self, context, requests, cancellation_context):
        """

        :param ResourceCommandContext context:
        :param str requests:
        :param CancellationContext cancellation_context:
        :return:
        """

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'GetVmDetails_context', context)
                self._log(logger, 'GetVmDetails_requests', requests)
                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                results = []

                requests_loaded = json.loads(requests)

                for request in requests_loaded[u'items']:
                    vm_name = request[u'deployedAppJson'][u'name']
                    vm_uid = request[u'deployedAppJson'][u'vmdetails'][u'uid']

                    result = nutanix_service.get_vm_details(vm_name, vm_uid)
                    results.append(result)

                result_json = json.dumps(results, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))

                self._log(logger, 'GetVmDetails_result', result_json)

                return result_json

    def remote_refresh_ip(self, context, ports, cancellation_context):
        """
        Will update the address of the computer resource on the Deployed App resource in cloudshell
        :param ResourceRemoteCommandContext context:
        :param ports:
        :param CancellationContext cancellation_context:
        :return:
        """

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                self._log(logger, 'remote_refresh_ip_context', context)
                self._log(logger, 'remote_refresh_ip_ports', ports)
                self._log(logger, 'remote_refresh_ip_cancellation_context', cancellation_context)
                cloud_provider_resource = Nutanixshell.create_from_context(context)

                decrypted_pass = cloudshell_session.DecryptPassword(cloud_provider_resource.password).Value

                nutanix_service = NutanixService(context.resource.address, cloud_provider_resource.user, decrypted_pass)

                deployed_app_dict = json.loads(context.remote_endpoints[0].app_context.deployed_app_json)
                remote_ep = context.remote_endpoints[0]
                deployed_app_private_ip = remote_ep.address
                deployed_app_public_ip = None

                resource_attributes = self._parse_attributes(deployed_app_dict['attributes'])

                public_ip_att = self._get_custom_attribute(resource_attributes, 'Public IP', None)
                ip_regex = self._get_custom_attribute(resource_attributes, 'IP Regex', '.*')
                refresh_ip_timeout = self._get_custom_attribute(resource_attributes, 'Refresh IP Timeout', 600)

                if public_ip_att:
                    deployed_app_public_ip = public_ip_att['value']

                deployed_app_fullname = remote_ep.fullname
                vm_uid = deployed_app_dict['vmdetails']['uid']

                nutanix_service.refresh_ip(cloudshell_session, deployed_app_fullname, vm_uid, deployed_app_private_ip,
                                           deployed_app_public_ip, ip_regex, refresh_ip_timeout)

    # </editor-fold>


    ### NOTE: According to the Connectivity Type of your shell, remove the commands that are not
    ###       relevant from this file and from drivermetadata.xml.

    # <editor-fold desc="Mandatory Commands For L2 Connectivity Type">

    def ApplyConnectivityChanges(self, context, request):
        """
        Configures VLANs on multiple ports or port-channels
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str request: A JSON string with the list of requested connectivity changes
        :return: a json object with the list of connectivity changes which were carried out by the driver
        :rtype: str
        """
        pass

    # </editor-fold>

    def SetAppSecurityGroups(self, context, request):
        """

        :param ResourceCommandContext context:
        :param str request:
        :return:
        :rtype: str
        """
        pass

    # </editor-fold>

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files, etc.
        """
        pass

    def _log(self, logger, name, obj):

        if not obj:
            logger.info(name + 'Value  is None')

        if not self._is_primitive(obj):
            name = name + '__json_serialized'
            obj = json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))

        logger.info(name)
        logger.info(obj)

    @staticmethod
    def _is_primitive(thing):
        primitive = (int, str, bool, float, unicode)
        return isinstance(thing, primitive)

    @staticmethod
    def _parse_attributes(attributes):
        result = dict()

        for each in attributes:
            result[each['name']] = each['value']

        return result

    @staticmethod
    def _get_custom_attribute(attributes, name, default):
        result = default

        if name in attributes:
            result = attributes[name]

        return result