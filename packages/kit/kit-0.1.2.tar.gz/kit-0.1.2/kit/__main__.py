#!/usr/bin/env python

"""Kit command line tool.

There are currently 4 commands available via the command tool, all
detailed below.

All commands accept an optional argument ``-c, --conf``
to indicate the path of the configuration file to use. If none is specified
Kit will search in the current directory for possible matches. If a single
file ``.cfg`` file is found it will use it.

"""

if __name__ == '__main__':

  from kit.commands import parser

  parsed_args = parser.parse_args()
  parsed_args.handler(parsed_args)

