from ConfigParser import ConfigParser
import sys
import logging
import inject

class Configuration(ConfigParser):    
    @inject.param('configfile')
    def __init__(self, configfile):
        self.cp = ConfigParser()
        self.logger = logging.getLogger(__name__)
        #ConfigParser.__init__(self)
        try:
            self.cp.readfp(open(configfile))
        except:
            self.logger.fatal("Could not open config file '{0}'.".format(configfile))
            sys.exit(2)
        for section in self.cp.sections():
            self.items(section) # this line will create cause a ValueError in case of config errors

    def items(self, section):
        # make the config a dict
        sectionConfigDict = {}
        for k, v in self.cp.items(section):
            sectionConfigDict[k] = v
        
        if self.cp.has_option(section, 'devices'):
            devicesConfigString =  self.cp.get(section, 'devices')
            # now overwrite the the config string with the parsed device list
            sectionConfigDict['devices'] = self.parseDevices(devicesConfigString, section)
        
        return sectionConfigDict
        
    def has_section(self, section):
        return self.cp.has_section(section)
    
    def parseDevices(self, configString, section):
        try:
            devices = eval(configString)
        except SyntaxError:
            raise ValueError('Could not parse "%s", is not a list.' % configString)
        if type(devices) is list:
            for device in devices:
                if type(device) is dict:
                    if not 'name' in device:
                        raise ValueError('Device "%s" in section "%s" does not contain a name.' % (device, section))
                    if not 'address' in device:
                        raise ValueError('Device "%s" in section "%s" does not contain a address.' % (device, section))
                    if not 'group' in device:
                        raise ValueError('Device "%s" in section "%s" does not contain a group.' % (device, section))
                    if not 'type' in device:
                        raise ValueError('Device "%s" in section "%s" does not contain a type.' % (device, section))
                else:
                    raise ValueError('Device config "%s" in section "%s" is not a dict.' % (device, section))
            return devices
        else:
            raise ValueError('Devices config "%s" in section "%s" is not a list.' % (configString, section))