from pydom.modules.ModuleBase import ModuleBase
import inject
import logging
import os
import imp
  
@inject.param('config')
def init_modules(config):
    modules = []

    import_modules()
    
    for module in ModuleBase.__subclasses__():
        init_module(config, modules, module)
    return modules

"""
This method will import any .py file from the modules directory except the file this code is in
and __init__ files.
"""
def import_modules():
    this_module = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
    module_location = os.path.dirname(os.path.realpath(__file__))
    for dirname, dirnames, filenames in os.walk(module_location):
        for file in filenames:
            mod_name,file_ext = os.path.splitext(os.path.split(file)[-1])
            if file_ext.lower() == '.py' and mod_name != this_module and mod_name !=  '__init__':
                path = os.path.normpath(dirname + os.sep + file)
                logging.getLogger(__name__).debug("Importing Module '{0}' from {1}".format(mod_name, path))
                imp.load_source(mod_name, path)

def init_module(config, modules, module):    
    if config.has_section(module.__name__):
        try:
            logging.getLogger(__name__).info("Initialising Module '{0}'".format(module.__name__))
            new_gateway = module(config.items(module.__name__))
            modules.append(new_gateway)
        except ValueError:
            logging.getLogger(__name__).error('could not initialise %s' % module.__name__)
