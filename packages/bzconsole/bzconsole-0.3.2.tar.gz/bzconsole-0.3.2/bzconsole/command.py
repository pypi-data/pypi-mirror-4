"""
a command-line interface to the command line, a la pythonpaste
"""

# TODO: move to http://k0s.org/hg/CommandParser/

import inspect
import json
import os
import sys
from optparse import OptionParser
from pprint import pprint

def read_dotfile():
    """read information from ~/.bz"""
    options = {}
    dotfile = os.path.join(os.environ['HOME'], '.bz')
    if not os.path.exists(dotfile):
        return {}
    f = file(dotfile)
    for line in f.readlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            key, value = [i.strip()
                          for i in line.split(':', 1)]
            options[key] = value
        else:
            print >> sys.stderr, "Bad option line: " + line
    return options

class Undefined(object):
  def __init__(self, default):
    self.default=default

class CommandParser(OptionParser):
    # TODO: add `help` command

    def __init__(self, _class, description=None):
        self._class = _class
        self.commands = {}
        usage = '%prog [options] command [command-options]'
        description = description or _class.__doc__
        OptionParser.__init__(self, usage=usage, description=description)
        commands = [ getattr(_class, i) for i in dir(_class)
                     if not i.startswith('_') ]
        commands = [ method for method in commands
                     if hasattr(method, '__call__') ]
        for _command in commands:
            c = self.command(_command)
            self.commands[c['name']] = c

        # get class options
        init = self.command(_class.__init__)
        self.command2parser(init, self)

        self.disable_interspersed_args()

    def add_option(self, *args, **kwargs):
        kwargs['default'] = Undefined(kwargs.get('default'))
        OptionParser.add_option(self, *args, **kwargs)

    def print_help(self):

        OptionParser.print_help(self)

        # short descriptions for commands
        command_descriptions = [dict(name=i,
                                     description=self.commands[i]['doc'].strip().split('\n',1)[0])
                                for i in self.commands.keys()]
        command_descriptions.append(dict(name='help', description='print help for a given command'))
        command_descriptions.sort(key=lambda x: x['name'])
        max_len = max([len(i['name']) for i in command_descriptions])
        description = "Commands: \n%s" % ('\n'.join(['  %s%s  %s' % (description['name'], ' ' * (max_len - len(description['name'])), description['description'])
                                                     for description in command_descriptions]))

        print
        print description

    def parse(self, args=sys.argv[1:]):
        """global parse step"""

        self.options, args = self.parse_args(args)

        # help/sanity check -- should probably be separated
        if not len(args):
            self.print_help()
            sys.exit(0)
        if args[0] == 'help':
            if len(args) == 2:
                if args[1] == 'help':
                    self.print_help()
                elif args[1] in self.commands:
                    name = args[1]
                    commandparser = self.command2parser(name)
                    commandparser.print_help()
                else:
                    self.error("No command '%s'" % args[1])
            else:
                self.print_help()
            sys.exit(0)
        command = args[0]
        if command not in self.commands:
            self.error("No command '%s'" % command)
        return command, args[1:]

    def invoke(self, args=sys.argv[1:]):
        """
        invoke
        """

        # parse
        name, args = self.parse(args)

        # setup
        options = read_dotfile()
        for key, value in self.options.__dict__.items():
            if isinstance(value, Undefined):
                if key in options:
                    continue
                options[key] = value.default
            else:
                options[key] = value
        _object = self._class(**options)

        # command specific args
        command = self.commands[name]
        commandparser = self.command2parser(name)
        command_options, command_args = commandparser.parse_args(args)
        if len(command_args) < len(command['args']):
            commandparser.error("Not enough arguments given")
        if len(command_args) != len(command['args']) and not command['varargs']:
            commandparser.error("Too many arguments given")

        # invoke the command
        retval = getattr(_object, name)(*command_args, **command_options.__dict__)
        if isinstance(retval, basestring):
            try:
                print retval
            except:
                print str(retval.encode('ascii', errors='ignore'))
        elif retval is None:
            pass
        elif isinstance(retval, list):
            for i in retval:
                print i
        elif isinstance(retval, dict):
            try:
                print json.dumps(retval, indent=2, sort_keys=True)
            except:
                pprint(retval)
        else:
            pprint(retval)
        return retval

    def command(self, function):
        name = function.func_name
        if function.__doc__:
            doc = inspect.cleandoc(function.__doc__)
        else:
            doc = ''
        argspec = inspect.getargspec(function)
        defaults = argspec.defaults
        if defaults:
            args = argspec.args[1:-len(defaults)]
            optional = dict(zip(argspec.args[-len(defaults):], defaults))
        else:
            args = argspec.args[1:]
            optional = None
        command = { 'doc': doc,
                     'name': name,
                     'args': args,
                     'optional': optional,
                     'varargs': argspec.varargs
                     }
        return command

    def commandargs2str(self, command):
        if isinstance(command, basestring):
            command = self.commands[command]
        retval = []
        retval.extend(['<%s>' % arg for arg in command['args']])
        varargs = command['varargs']
        if varargs:
            retval.append('<%s> [%s] [...]' % (varargs, varargs))
        if command['optional']:
            retval.append('[options]')
        return ' '.join(retval)

    def doc2arghelp(self, docstring, decoration='-', delimeter=':'):
        """
        Parse a docstring and get at the section describing arguments
        - decoration: decoration character
        - delimeter: delimter character

        Yields a tuple of the stripped docstring and the arguments help
        dictionary
        """
        lines = [ i.strip() for i in docstring.split('\n') ]
        argdict = {}
        doc = []
        option = None
        for line in lines:
            if not line and option: # blank lines terminate [?]
                break
            if line.startswith(decoration) and delimeter in line:
                name, description = line.split(delimeter, 1)
                name = name.lstrip(decoration).strip()
                description = description.strip()
                argdict[name] = [ description ]
                option = name
            else:
                if option:
                    argdict[name].append(line)
                else:
                    doc.append(line)
        argdict = dict([(key, ' '.join(value))
                        for key, value in argdict.items()])
        return ('\n'.join(doc), argdict)

    def command2parser(self, command, parser=None):
        if isinstance(command, basestring):
            command = self.commands[command]
        doc, argdict = self.doc2arghelp(command['doc'])
        if parser is None:
            parser = OptionParser('%%prog %s %s' % (command['name'], self.commandargs2str(command)),
                                  description=doc, add_help_option=False)
        if command['optional']:
            for key, value in command['optional'].items():
                help = argdict.get(key, '')
                if value is True:
                    parser.add_option('--no-%s' % key, dest=key,
                                      action='store_false', default=True,
                                      help=help)
                elif value is False:
                    parser.add_option('--%s' % key, action='store_true',
                                      default=False, help=help)
                elif type(value) in set([type(()), type([])]):
                    if value:
                        help += ' [DEFAULT: %s]' % value
                    parser.add_option('--%s' % key, action='append',
                                      default=list(value),
                                      help=help)
                else:
                    if value is not None:
                        help += ' [DEFAULT: %s]' % value
                    parser.add_option('--%s' % key, help=help, default=value)

        return parser
