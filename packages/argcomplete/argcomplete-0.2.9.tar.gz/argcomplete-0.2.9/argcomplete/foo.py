#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argcomplete, argparse

def myCompleter(*args, **kwargs):
    return ('C1', 'C2', 'C3', 'C4')

parser = argparse.ArgumentParser()
#parser.add_argument("foo", nargs="*").completer=myCompleter
#parser.add_argument("--bar", type=int)
parser.add_argument("--bar")
parser.add_argument("--env-var0", nargs=2).completer = argcomplete.completers.EnvironCompleter

parser.add_argument("--protocolz", choices=('http', 'https', 'ssh', 'rsync', 'wss'))
parser.add_argument("--protoz").completer=argcomplete.completers.ChoicesCompleter(('http', 'https', 'ssh', 'rsync', 'wss'))

'''
parser.add_argument("--env-var1").completer = argcomplete.completers.EnvironCompleter
parser.add_argument("--env-var2").completer = argcomplete.completers.EnvironCompleter

parser.add_argument("--bar", action='store_true')
parser.add_argument("--baz")
parser.add_argument("--xy-zzt", action='store_true')
'''

subparsers = parser.add_subparsers()
subparsers.metavar = 'command'

parser_wat = subparsers.add_parser('wat')
#parser.add_argument("foo").completer=myCompleter
parser_wat.add_argument('--token', help='Authentication token to use')
parser_wat.add_argument("foo", nargs="*").completer=myCompleter
parser_wat.add_argument('--host', help='Log into the given auth server host (port must also be given)')
parser_wat.add_argument('--port', type=int, help='Log into the given auth server port (host must also be given)')
p = parser_wat.add_argument('--protocol', help='Use the given protocol to contact auth server (by default, the correct protocol is guessed based on --port)',
    nargs='+', choices=['http', 'https', 'wss', 'ssh'])
parser_wat.add_argument('--noprojects', dest='projects', help='Do not print available projects', action='store_false')
parser_wat.add_argument('--save', help='Save token and other environment variables for future sessions', action='store_true')

parser_wheee = subparsers.add_parser('wheee')
parser_wheee.add_argument('--token', help='Authentication token to use')
parser_wheee.add_argument('--host', help='Log into the given auth server host (port must also be given)')
parser_wheee.add_argument('--port', type=int, help='Log into the given auth server port (host must also be given)')
parser_wheee.add_argument('--protocol', help='Use the given protocol to contact auth server (by default, the correct protocol is guessed based on --port)',
    nargs='+', choices=['http', 'https', 'wss', 'ssh'])
parser_wheee.add_argument('--noprojects', dest='projects', help='Do not print available projects', action='store_false')
parser_wheee.add_argument('--save', help='Save token and other environment variables for future sessions', action='store_true')

parser_stuff = subparsers.add_parser('stuff')
parser_stuff.add_argument('--token', help='Authentication token to use')
parser_stuff.add_argument('--host', help='Log into the given auth server host (port must also be given)')
parser_stuff.add_argument('--port', type=int, help='Log into the given auth server port (host must also be given)')
parser_stuff.add_argument('--protocol', help='Use the given protocol to contact auth server (by default, the correct protocol is guessed based on --port)',
    choices=['http', 'https'])
parser_stuff.add_argument('--noprojects', dest='projects', help='Do not print available projects', action='store_false')
parser_stuff.add_argument('--save', help='Save token and other environment variables for future sessions', action='store_true')

# s2 = parser_wat.add_subparsers()
# s2p = s2.add_parser('wut')
# s2p.add_argument('--w00tz', action='store_true')

def main():
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    print args

