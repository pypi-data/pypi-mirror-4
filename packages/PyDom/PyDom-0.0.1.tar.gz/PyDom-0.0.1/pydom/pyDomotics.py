from pydom.Configuration import Configuration
from pydom.Command import Command
from pydom.Dispatcher import Dispatcher
from pydom.DeviceManager import DeviceManager
import pydom.gateways.GatewayFactory as GatewayFactory
import pydom.modules.ModuleFactory as ModuleFactory
import inject
import logging
import logging.config
import cherrypy
import simplejson
import os
import sys
from optparse import OptionParser

__version__ = '0.0.1'
__date__ = '2013-04-13'
__updated__ = '2013-04-13'

"""Init method. Starts all gateways started"""
@inject.param('gateways')
@inject.param('modules')
@inject.param('devManager')
def initApplication(gateways, modules, devManager):
    pass

WEB_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), u"web")

class App(object):
    @cherrypy.expose
    def index(self):
        return open(os.path.join(WEB_DIR, u'index.html'))
    
    @cherrypy.expose
    def doCommand(self, devices, action):    
        message = ''
        try:
            deviceList = []
            deviceList = devices.split(',')
            command = Command(deviceList, action)
            self.send_command(command)
            message = "Executing command: '" + command.__str__() + "'"
        except Exception, e:
            logging.exception(e)
            message = e.message

        return message

    @cherrypy.expose
    @inject.param('devManager')
    def deviceList(self, devManager):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.json_repr(devManager.devices)

    @inject.param('dispatcher')
    def send_command(self, command, dispatcher):
        dispatcher.enqueue(command)
        
    def json_repr(self, obj):
        """Represent instance of a class as JSON.
        Arguments:
        obj -- any object
        Return:
        String that reprent JSON-encoded object.
        """
        def serialize(obj):
            """Recursively walk object's hierarchy."""
            if isinstance(obj, (bool, int, long, float, basestring)):
                return obj
            elif isinstance(obj, dict):
                obj = obj.copy()
                for key in obj:
                    obj[key] = serialize(obj[key])
                return obj
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(serialize([item for item in obj]))
            elif hasattr(obj, '__dict__'):
                return serialize(obj.__dict__)
            else:
                return repr(obj) # Don't know how to handle, convert to string
        return simplejson.dumps(serialize(obj))

def main(argv=None):   
    if argv is None:
        argv = sys.argv[1:]
    opts = parseOptions(argv)
    
    try:
        logging.config.fileConfig(opts.logconfigfile)
    except:
        print "Could not parse logging config file '{0}', using defaults.".format(opts.logconfigfile)
    
    logger = logging.getLogger(__name__)
#    
    logger.debug('Initializing')
    injector = inject.Injector()
    injector.bind('configfile', to=opts.configfile)
    injector.bind('config', to=Configuration, scope=inject.appscope)
    injector.bind('gateways', to=GatewayFactory.init_gateways, scope=inject.appscope)
    injector.bind('modules', to=ModuleFactory.init_modules, scope=inject.appscope)
    injector.bind('devManager', to=DeviceManager, scope=inject.appscope)
    injector.bind('dispatcher', to=Dispatcher, scope=inject.appscope)
    inject.register(injector)
    
    initApplication()

    config = {'/web':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': WEB_DIR,
                }
        }    
    
    logger.debug('Starting webserver')
    try:
        cherrypy.tree.mount(App(), '/', config=config)
        cherrypy.server.socket_port = 8000
        cherrypy.engine.start()
    except KeyboardInterrupt:
        cherrypy.engine.stop()

def parseOptions(argv):
    program_name = os.path.basename(sys.argv[0])
    program_version = __version__
    program_build_date = "%s" % __updated__
 
    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2013 Jos (CircuitDB.com)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"
    
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-c", "--config", dest="configfile", help="specifies the config file [default: %default]", metavar="FILE")
        parser.add_option("-l", "--logconf", dest="logconfigfile", help="specifies the config file for logging [default: %default]", metavar="FILE")
#        parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        
        # set defaults
        parser.set_defaults(configfile=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pyDomotics.cfg'), logconfigfile=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging.conf'))
        
        # process options        
        (opts, args) = parser.parse_args(argv)

        return opts
        
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == '__main__':
    sys.exit(main())