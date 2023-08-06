#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import argparse

from configobj import ConfigObj
from validate import Validator
from commodity.pattern import MetaBunch
from commodity.type_ import module_to_dict

import config

defaults = ConfigObj(configspec=file('config.spec'))
defaults.validate(Validator(), copy=True)

defa = MetaBunch(defaults)

parser = argparse.ArgumentParser(prog='prego', prefix_chars='+-')

# behaviour
parser.add_argument('+k', '++keep-going', action='store_true',
                    help="continue even with failed assertion or tests")

parser.add_argument('+d', '++dirty', action='store_true',
                    help="do not remove generated files")

# output
parser.add_argument('+o', '++stdout', action='store_true',
                    help='print tests stdout')
parser.add_argument('+e', '++stderr', action='store_true',
                    help='print tests stderr')
parser.add_argument('+v', '++verbose', dest='verbosity', action='count',
                    help='increase log verbosity')

# styling
parser.add_argument('+p', '++plain', action='store_false', dest='color',
                    help='avoid colors and styling in output')

opts, args = parser.parse_known_args(namespace=defa)

print opts
for key, value in opts.items():
    setattr(config, key, value)

print module_to_dict(config), args
