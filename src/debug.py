import mock
from driver import NutanixshellDriver
from cloudshell.shell.core.driver_context import InitCommandContext, AutoLoadCommandContext, ResourceCommandContext, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext, ResourceRemoteCommandContext
from sdk.nutanix_service import *


context = mock.create_autospec(ResourceCommandContext)
context.resource = mock.MagicMock()
context.reservation = mock.MagicMock()
context.connectivity = mock.MagicMock()
context.reservation.reservation_id = "a-a-a-a"
# context.resource.address = "1.2.3.4"
context.resource.name = "nutanix"
context.resource.attributes = dict()
shell_name = "Nutanixshell"
context.resource.attributes["{}.User".format(shell_name)] = "cidapiuser"
context.resource.attributes["{}.Password".format(shell_name)] = "C1dAp1user"
context.resource.attributes["{}.address".format(shell_name)] = "10.154.3.20"


#driver = NutanixshellDriver()
# print driver.run_custom_command(context, custom_command="sh run", cancellation_context=cancellation_context)
#driver.initialize(context)
#result = driver.get_inventory(context)

request = """{
   "driverRequest":{
      "actions":[
         {
            "actionParams":{
               "appName":"my new app",
               "deployment":{
                  "deploymentPath":"Nutanixshell.DefaultDeployPath",
                  "attributes":[
                     {
                        "attributeName":"Nutanixshell.DefaultDeployPath.Wait for IP",
                        "attributeValue":"True",
                        "type":"attribute"
                     },
                     {
                        "attributeName":"Nutanixshell.DefaultDeployPath.Autoload",
                        "attributeValue":"True",
                        "type":"attribute"
                     },
                     {
                        "attributeName":"Nutanixshell.DefaultDeployPath.Nutanix Image Path",
                        "attributeValue":"folder1/image2",
                        "type":"attribute"
                     }
                  ],
                  "type":"deployAppDeploymentInfo"
               },
               "appResource":{
                  "attributes":[
                     {
                        "attributeName":"Password",
                        "attributeValue":"3M3u7nkDzxWb0aJ/IZYeWw==",
                        "type":"attribute"
                     },
                     {
                        "attributeName":"Public IP",
                        "attributeValue":"",
                        "type":"attribute"
                     },
                     {
                        "attributeName":"User",
                        "attributeValue":"user1",
                        "type":"attribute"
                     }
                  ],
                  "type":"appResourceInfo"
               },
               "type":"deployAppParams"
            },
            "actionId":"c5a74c4d-5f9e-468b-9e15-d0c902ca09f2",
            "type":"deployApp"
         }
      ]
   }
}"""

for i in range(1):
    print i


print "done"


