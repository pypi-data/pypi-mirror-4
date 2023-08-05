#!/usr/local/bin/python

from magma.commands import command_manager
import sys

command_manager.execute(sys.argv[1:])
