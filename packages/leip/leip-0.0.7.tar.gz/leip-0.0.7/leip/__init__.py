#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Leip
"""

import argparse
from collections import defaultdict
import logging
import os
import sys
import textwrap

import Yaco

logging.basicConfig()
lg = logging.getLogger(__name__)
#lg.setLevel(logging.DEBUG)

class app(object):

    def __init__(self, name=None, config_files = None, set_name = 'set',
                 base_config = ""):
        """

        :param name: base name of the applications
        :type name: string
        :param config_files: list of configuration files, if ommitted 
             the app defaults to `/etc/<NAME>.yaml` and 
             `~/.config/<NAME>/config.yaml`. The order is important, the last
             config file is the one to which changes will be saved
        :type config_files: a list of tuples: (id, filename)
        :param set_name: name of the command to set new values, default='set'
        :type set_name: string

        :param base_config: basis configuration on top of which the
           rest is loaded. This allows a developer to, for example,
           extra a default configuration from a pacakge
        :type base_config: yaml string
        """

        if name is None:
            name = os.path.basename(sys.argv[0])
            
        lg.debug("Starting Leip app")
        self.leip_commands = {}
        self.plugins = {}
        self.hooks = defaultdict(list)

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('-v', '--verbose', action='store_true')

        self.subparser = self.parser.add_subparsers(
            title = 'command', dest='command')

        #configuration object
        if not config_files:
            config_files = (
                ('app1', sys.argv[0] + '.config'),
                ('system', '/etc/{0}.config'.format(name)),
                ('user', '~/.config/{0}/{0}.config'.format(name)),
                )

        #contains transient data - execution specific
        self.trans = Yaco.Yaco()

        #contains configuration data
        self.conf = Yaco.PolyYaco(name, base = base_config, files = config_files)
        self.conf.load()

        #create a 'set' command to manipulate the configuration
        def _conf_set(app, args):
            """
            Set & save a configuration value
            """
            self.conf[args.key] = args.value
            self.conf.save()

        #annotate the function for later use as command
        _conf_set._leip_command = set_name
        _conf_set._leip_args = [
            [['key'], {'help' : "key to set"}],
            [['value'], {'help' : "value to set the key to"}],
            ]
        
        self.register_command(_conf_set)

        #check for plugins
        if 'plugin' in self.conf:
            for plugin_name in self.conf.plugin:
                lg.debug("loading plugin %s" % plugin_name)
                
                module_name = self.conf.plugin[plugin_name].module.strip()

                enabled = self.conf.plugin[plugin_name].get('enabled', True)
                if not enabled: 
                    continue


                lg.debug("attempting to load plugin from module {0}".format(
                    module_name))
                modbase, modsub = module_name.rsplit('.', 1)
                package = __import__( modbase, globals(), locals(), [modsub] )
                mod = package.__dict__[modsub]

                #weird - this does not seem to work
                #modsearch = imp.find_module(module_name)
                #module = imp.load_module(module_name, *modsearch)

                self.plugins[plugin_name] = mod
                self.discover(mod)
        

        #register command run as a hook
        def _run_command(app):
            command = self.trans.args.command
            self.leip_commands[command](self, self.trans.args)
        self.register_hook('run', 50, _run_command)
        
        #register parse arguments as a hook
        def _prep_args(app):
            self.trans.args = self.parser.parse_args()
            if self.trans.args.verbose:
                rootlogger = logging.getLogger()
                rootlogger.setLevel(logging.DEBUG)

        self.register_hook('prepare', 50, _prep_args)

        #hook run order
        self.hook_order = ['prepare', 'run', 'finish']

        
    def discover(self, mod):
        """
        discover all hooks & commands in the provided module or 
        module namespace (globals())

        :param mod: an imported module or a globals dict
        """
        
        if isinstance(mod, dict):
            mod_objects = mod
        else:
            mod_objects = mod.__dict__

        for obj_name in mod_objects:
            obj = mod_objects[obj_name]
            
            #see if this is a function decorated as hook
            if not hasattr(obj, '__call__'):
                continue

            if hasattr(obj, '_leip_hook'):
                hook = obj._leip_hook
                prio = obj._leip_hook_priority
                lg.debug("discovered hook %s (%d) in %s" % (
                        hook, prio, obj.__name__))
                self.hooks[hook].append(
                    (prio, obj))
            
            if hasattr(obj, '_leip_command'):
                self.register_command(obj)

    def register_command(self, function):
        cname = function._leip_command
        lg.debug("discovered command %s" % cname)

        self.leip_commands[cname] = function

        #create a help text from the docstring - if possible
        _desc = [cname]
        if function.__doc__:
            _desc = function.__doc__.strip().split("\n", 1)

        if len(_desc) == 2:
            shortDesc, longDesc = _desc
        else:
            shortDesc, longDesc = _desc[0], ""

        longDesc = textwrap.dedent(longDesc)

        cp = self.subparser.add_parser(cname, help=shortDesc,
                                       description=longDesc)

        for args, kwargs in function._leip_args:
            cp.add_argument(*args, **kwargs)

        function._cparser = cp

        
    def register_hook(self, name, priority, function):
        lg.debug("registering hook {0} / {1}".format(name, function))
        self.hooks[name].append(
            (priority, function))

    def run_hook(self, name, *args, **kw):
        """
        Execute hook
        """
        to_run = sorted(self.hooks[name])
        lg.debug("running hook %s" % name)
        for priority, func in to_run:
            lg.debug("running hook %s" % func)
            func(self, *args, **kw)

    def run(self):
        for hook in self.hook_order:
            self.run_hook(hook)
        




## 
## Command decorators
##

def command(f):
    """
    Tag a function to become a command - take the function name and
    use it as the name of the command.
    """
    f._leip_command = f.__name__
    f._leip_args = []
    lg.debug("marking function as leip command: %s" % f.__name__)
    return f
    
def commandName(name):
    """
    as command, but provide a specific name
    """
    def decorator(f):
        lg.debug("marking function as leip command: %s" % name)
        f._leip_command = name
        f._leip_args = []
        return f
    return decorator

def arg(*args, **kwargs):
    """
    add an argument to a command - use the full argparse syntax
    """
    def decorator(f):
        lg.debug("adding leip argument {0}, {1}".format(str(args), str(kwargs)))
        f._leip_args.append((args, kwargs))
        return f
    return decorator

def flag(self, *args, **kwargs):
    """
    Add a flag to (default false - true if specified) any command
    """
    def decorator(f):
        kwargs['action'] = kwargs.get('action', 'store_true')
        kwargs['default'] = kwargs.get('default', False)
        f._cparser.add_argument(*args, **kwargs)
        return f
    return decorator

    
##
## Hook decorators
##

def hook(name, priority = 50):
    """
    mark this function as a hook for later execution

    :param name: name of the hook to call
    :type name: string
    :param priority: inidicate how soon this hook must be called.
        Higher is sooner (default: 50)
    :type priority: int
    """
    def _hook(f):
        lg.debug("registering '%s' hook in %s priority %d" % (
                name, f.__name__, priority))
        f._leip_hook = name
        f._leip_hook_priority = priority
        return f
    
    return _hook

    
    
        
        
