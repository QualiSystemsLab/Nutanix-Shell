# Nutanix-Shell

A repository for a Nutanix-v2.0 Cloud Provider.
Does not have connectivity functionality implemented. This Nutanix CP was developed for a use case where VMs were cloned and kept the existing connectivity settings.

## Projects
* **Deployment Drivers**

    These projects extend CloudShell apps with new deployment types
    * **Nutanix_Clone_From_VM**
    App deployment type driver for creating clones from existing VMs


* **package**

    The Nutanic-v2.0 Cloud Provider package can be found in the [release section of our Github repo](https://github.com/QualiSystemsLab/Nutanix-Shell/releases)

* **driver.py**

    The CloudShell driver for controlling Nutanix-v2.0 via CloudShell. Basic cloud provider driver, leverages nutanix_service.py for most funtionality.

* **nutanix_service.py**

    Class containing the methods making REST API calls to the Nutanix-v2.0 host.

## Installation
* [QualiSystems CloudShell](http://www.qualisystems.com/products/cloudshell/cloudshell-overview/)


## Getting Started

1. Download NutanixShell.zip from Releases page
2. Drag it into your CloudShell Portal
3. Set Nutanix connection details on the Nutanix resource according to your environment.
4. Update VM Deployment App to set correct "Cloned VM UUID" attribute according to your environment.
4. Reserve Virtualisation Starter environment
5. Add VM Deployment from App/Services for each required virtual application
8. Run Deploy command on each VM Deployment

## License
[Apache License 2.0](https://github.com/QualiSystems/vCenterShell/blob/master/LICENSE)