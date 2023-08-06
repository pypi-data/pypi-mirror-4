from pydom.gateways.GatewayBase import GatewayBase
import inject
import logging
import os
import imp
  
@inject.param('config')
def init_gateways(config):
    gateways = []

    import_gateways()
    
    for gateway in GatewayBase.__subclasses__():
        init_gateway(config, gateways, gateway)
    return gateways

"""
This method will import any .py file from the gateways directory except the file this code is in
and __init__ files.
"""
def import_gateways():
    this_module = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
    gateway_module_location = os.path.dirname(os.path.realpath(__file__))
    for dirname, dirnames, filenames in os.walk(gateway_module_location):
        for file in filenames:
            mod_name,file_ext = os.path.splitext(os.path.split(file)[-1])
            if file_ext.lower() == '.py' and mod_name != this_module and mod_name !=  '__init__':
                path = os.path.normpath(dirname + os.sep + file)
                logging.getLogger(__name__).debug("Importing Gateway '{0}' module from {1}".format(mod_name, path))
                imp.load_source(mod_name, path)

def init_gateway(config, gateways, gateway):    
    if config.has_section(gateway.__name__):
        try:
            logging.getLogger(__name__).info("Initialising Gateway '{0}'".format(gateway.__name__))
            new_gateway = gateway(config.items(gateway.__name__))
            gateways.append(new_gateway)
            new_gateway.start()
        except ValueError:
            logging.getLogger(__name__).error('could not initialise %s' % gateway.__name__)
