
from pyvisdk.base.managed_object_types import ManagedObjectTypes

from pyvisdk.base.base_entity import BaseEntity

import logging

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

class EnvironmentBrowser(BaseEntity):
    '''This managed object type provides access to the environment that a
    ComputeResource presents for creating and configuring a virtual machine.The
    environment consists of three main components:'''

    def __init__(self, core, name=None, ref=None, type=ManagedObjectTypes.EnvironmentBrowser):
        super(EnvironmentBrowser, self).__init__(core, name=name, ref=ref, type=type)

    
    @property
    def datastoreBrowser(self):
        '''DatastoreBrowser to browse datastores that are available on this entity.'''
        return self.update('datastoreBrowser')

    
    
    def QueryConfigOption(self, key, host):
        '''Query for a specific virtual machine configuration option (the
        ConfigOption).Query for a specific virtual machine configuration option (the
        ConfigOption).Query for a specific virtual machine configuration option (the
        ConfigOption).
        
        :param key: The key found in the VirtualMachineConfigOptionDescriptor, obtained by invoking the QueryConfigOptionDescriptor operation.
        
        :param host: The host whose ConfigOption is requested.
        
        '''
        return self.delegate("QueryConfigOption")(key, host)
    
    def QueryConfigOptionDescriptor(self):
        '''The list of ConfigOption keys available on this entity.
        
        '''
        return self.delegate("QueryConfigOptionDescriptor")()
    
    def QueryConfigTarget(self, host):
        '''Queries for information about a specific target, a "physical" device that can
        be used to back virtual devices. The ConfigTarget that is returned specifies
        the set of values that can be used in the device backings to connect the
        virtual machine to physical (or logical) host devices.Queries for information
        about a specific target, a "physical" device that can be used to back virtual
        devices. The ConfigTarget that is returned specifies the set of values that can
        be used in the device backings to connect the virtual machine to physical (or
        logical) host devices.Queries for information about a specific target, a
        "physical" device that can be used to back virtual devices. The ConfigTarget
        that is returned specifies the set of values that can be used in the device
        backings to connect the virtual machine to physical (or logical) host devices.
        
        :param host: If specified, the host whose default BackingInfo is requested.
        
        '''
        return self.delegate("QueryConfigTarget")(host)
    
    def QueryTargetCapabilities(self, host):
        '''Queries for information on the capabilities supported by the ComputeResource
        associated with the EnvironmentBrowser.Queries for information on the
        capabilities supported by the ComputeResource associated with the
        EnvironmentBrowser.Queries for information on the capabilities supported by the
        ComputeResource associated with the EnvironmentBrowser.
        
        :param host: If specified, the host whose capabilities are requested.
        
        '''
        return self.delegate("QueryTargetCapabilities")(host)