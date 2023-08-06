'''
Mercurial like commands definition
'''
from __future__ import print_function

import inspect
import os
import optparse
import re
import shlex
import sys

from ConfigParser import ConfigParser
from collections import Mapping

try:
    from collections import OrderedDict as ConfigDict
except ImportError:
    try:
        from ordereddict import OrderedDict as ConfigDict
    except ImportError:
        ConfigDict = dict

INVALID_USAGE = 64
ABORTED = 1

class Abort(Exception):
    pass

class InvalidUsage(Exception):
    pass
   
class OptionParser(optparse.OptionParser):
    def error(self, msg):
        raise InvalidUsage(msg)

class BaseUi(object):
    DebugLevel = SILENT, NORMAL, VERBOSE, DEBUG = range(4)
    
    def __init__(self, config=None):
        self.mode = self.NORMAL
        self.config = config
        
    def write(self, *msg):
        if self.is_enabled(self.SILENT):
            self._write_to(sys.stdout, *msg)
        
    def status(self, *msg):
        if self.is_enabled(self.NORMAL):
            self._write_to(sys.stderr, *msg)
    
    def note(self, *msg):
        if self.is_enabled(self.VERBOSE):
            self._write_to(sys.stderr, *msg)
        
    def debug(self, *msg):
        if self.is_enabled(self.DEBUG):
            self._write_to(sys.stderr, *msg)
    
    def warn(self, *msg):
        self._write_to(sys.stderr, *msg)
        
    def is_enabled(self, level):
        return self.mode >= level
        
    def flush(self):
        sys.stdout.flush()
        sys.stderr.flush()
    
    def _write_to(self, file, *msg):
        for m in msg:
            file.write(str(m))
            
    def has_config(self, section=None, key=None):
        return self.config and self.config.contains(section, key)
        
    def get_config(self, section, key, default=None):
        if self.config and self.config.contains(section, key):
            return self.config.get(section, key)
        return default
        
    def set_config(self, section, key, value):
        if self.config and hasattr(self.config, 'set'):
            self.config.set(section, key, value)
            return True
        return False
        
    def get_config_items(self, section):
        if self.config  and self.config.contains(section):
            return list(self.config.items(section))
        return []
        
    def flush_config(self):
        if self.config and hasattr(self.config, 'save'):
            self.config.save()
            return True
        return False
  
class DictConfig(object):
    def __init__(self, data):
        self._data = data
        
    def get(self, section, key):
        return self._data[section][key]
        
    def items(self, section):
        return self._data.get[section].items()
    
    def contains(self, section, key=None):
        if not section in self._data:
            return False
        if key != None:
            return key in self._data[section]
        return True
    
class FileConfig(object):   
    def __init__(self, file_path):
        self._file_path = file_path
        
        self._config = ConfigParser(dict_type=ConfigDict)
        self._config.read(file_path)
    
    def get(self, section, key):
        return self._config.get(section, key, None)
        
    def set(self, section, key, value):
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, value)
        
    def items(self, section):
        return self._config.items(section)
        
    def contains(self, section, key=None):
        if not self._config.has_section(section):
            return False
        if key != None:
            return self._config.has_option(section, key)
        return True
            
    def save(self):
        self._config.write(open(self._file_path, 'w'))

class Command(object):
    def __init__(self, function, names, switches, usage, proxy=None):
        self.function = function
        self.names = names
        self.switches = switches
        self.proxy = proxy
        
        if function.__doc__:
            self.doc = function.__doc__.strip()
        else:
            self.doc = ''
        
        self.usage = usage        
        
    def _create_parser(self, appname):
        usage = self.usage
        if len(self.names) > 1:
            usage += '\n\nAliases: ' + ', '.join(self.names[1:])
        usage += '\n\n' + self.doc
        
        parser = OptionParser(usage=usage)
        
        for short_name, long_name, default_value, description in self.switches:
            names = []
            if short_name:
                names.append('-' + short_name)
            if long_name:
                names.append('--' + long_name)
            
            long_name = long_name.replace('-', '_')
            options = {
                'dest': long_name,
                'help': description,
                'default': default_value
            }
            
            if default_value is False:
                options['action'] = 'store_true'
            
            parser.add_option(*names, **options)
            
        return parser
        
    def __call__(self, ui, appname, args):
        parser = self._create_parser(appname)
        
        try:
            (options, args) = parser.parse_args(list(args))
            options = options.__dict__
            
            if self.proxy:
                res = self.proxy(self.function, ui, *args, **options)
            else:
                res = checked_command_call(self.function, ui, *args, **options)
            
            try:
                res = int(res)
            except TypeError:
                res = int(bool(res))
                
            return res
            
        except Abort, e:
            ui.warn('Abort: ', e, '\n')
            return ABORTED
        except InvalidUsage, e:
            ui.warn('Invalid usage: ', e, '\n\n')
            ui.status(parser.format_help().rstrip(), '\n')
            return INVALID_USAGE
        except KeyboardInterrupt:
            ui.warn('Interrupted!', '\n')
            return ABORTED
        except Exception, e:
            ui.warn('Unexpected error. Exiting.', '\n')
            raise
    
def checked_command_call(func, *args, **kwargs):
    spec = inspect.getargspec(func)
    
    if spec.varargs or (len(args) == len(spec.args)):
        pass
    elif spec.defaults == None or (len(args) + len(spec.defaults) != len(spec.args)):
        # not counting with keywords at all here
        raise InvalidUsage('Invalid number of arguments.')
    
    return func(*args, **kwargs)
    
_default_cmdtable = {}
     
def register(name, switches, usage, proxy=None, cmdtable=_default_cmdtable):
    '''registers a command into cmdtable
    '''    
    def register(function):
        names = name.split('|')
        cmd = Command(function, names, switches, usage=usage, proxy=proxy)
        for n in names:
            if n in cmdtable:
                msg = "Ignoring duplicate command name '{0}'".format(n)
                if n != names[0]:
                    msg += " used as alias for '{0}'".format(names[0])
                msg += "."
                print(msg, file=sys.stderr)
            else:
                cmdtable[n] = cmd
            
    return register
    
ui_opts = [
    ('', 'silent', False, 'silent output mode'),
    ('', 'verbose', False, 'verbose output mode'),
    ('', 'debug', False, 'debug output mode'),
]

def process_ui_opts(ui, opts):
    if opts.pop('silent', False): ui.mode = BaseUi.SILENT
    if opts.pop('verbose', False): ui.mode = BaseUi.VERBOSE
    if opts.pop('debug', False): ui.mode = BaseUi.DEBUG
    
    return ui, opts

def ui_proxy(func, ui, *args, **opts):
    ui, opts = process_ui_opts(ui, opts)
    
    return checked_command_call(func, ui, *args, **opts)
    
def register_with_ui_opts(name, switches, usage, proxy=ui_proxy, cmdtable=_default_cmdtable):
    '''registers a command into cmdtable adding options for BaseUi
    '''
    return register(name=name, switches=switches+ui_opts, usage=usage, proxy=proxy, cmdtable=cmdtable)

def run(ui, appname, args, cmdtable=_default_cmdtable, aliases={}, defaults={}):
    '''runs a command from cmdtable according to what was passed in args
    '''
    appname = os.path.basename(appname)
    
    assert isinstance(cmdtable, Mapping)
    assert isinstance(aliases, Mapping)
    assert isinstance(defaults, Mapping)
       
    for name in aliases.keys():
        if name in cmdtable:
            ui.warn("Ignoring alias definition '{0}' which overrides already defined command name.\n".format(name))
            aliases = dict(aliases)
            del aliases[name]
    
    # add help command
    def help_proxy(func, *args, **options):
        return checked_command_call(func, args[0], cmdtable, appname, *args[1:], **options)
    if not 'help' in cmdtable:
        register('help', [], '%prog help [COMMAND]', proxy=help_proxy, cmdtable=cmdtable)(help)
        
    # special cmdname values
    duplicate_name = ""
    
    # retrieve command:
    result = 0
    if args:  
        cmdname = args.pop(0)
        if cmdname in ['-h', '--help']:
            cmdname = 'help' 
    else:
        cmdname = None
        result = INVALID_USAGE
    
    # check the command
    cmd = cmdtable.get(cmdname)
    if cmdname and not cmd and not cmdname in aliases:
        duplicates = []
        partial_name = cmdname
        resolved_name = None
        command_names = cmdtable.keys() + aliases.keys()
        for name in command_names:
            if name.startswith(partial_name):
                if resolved_name:
                    # check if this is not an alias
                    if cmdtable.get(name, name) is not cmdtable.get(resolved_name, resolved_name):
                        duplicates.append(name)
                else:
                    resolved_name = name
                    duplicates.append(name)
        if len(duplicates) == 1:
            cmdname = resolved_name
        elif len(duplicates) > 1:
            ui.warn("Command '{0}' is ambiguous: {1}".format(partial_name, ', '.join(duplicates)), '\n\n')
            cmdname = duplicate_name  
            
    if cmdname in defaults:
            default_args = shlex.split(defaults[cmdname])
    else:
        default_args = []
    
    if cmdname in aliases:
        alias_args = shlex.split(aliases[cmdname])
        cmdname = alias_args[0]
        alias_args = alias_args[1:]
    else:
        alias_args = []
        
    args = alias_args + default_args + args
    
    cmd = cmdtable.get(cmdname)
    
    if not cmd:
        if not cmdname:
            ui.warn("No command specified", '\n\n')
        elif cmdname is not duplicate_name:
            ui.warn("Uknown command '{0}'".format(cmdname), '\n\n')
        
        cmdname = 'help'
        cmd = cmdtable[cmdname]
        result = INVALID_USAGE
    
    cmdresult = cmd(ui, appname, args)
    
    return cmdresult if result == 0 else result

def help(ui, cmdtable, appname, cmdname=None, **options):
    '''print command help
    '''
    if cmdname:
        return run(ui, cmdtable, appname, [cmdname, '--help'])
    
    ui.write(
        'Usage: {0} COMMAND [OPTION]... [ARGUMENT]...'.format(appname), '\n',
        '\n', 
        'Commands:', '\n')

    commads = set(cmdtable.itervalues())
    commads = sorted(commads, key=lambda cmd: cmd.names[0])
    
    max_len = max(len(cmd.names[0]) for cmd in commads)
    
    for cmd in commads:
        ui.write(' ', cmd.names[0].ljust(max_len), '  ', cmd.doc.split('\n')[0], '\n')
        
    ui.write(
        '\nUse "{0} help COMMAND" or "{0} COMMAND --help" to display command specific help.'.format(appname),
        '\n')
