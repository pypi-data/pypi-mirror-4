#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bake any script that imports this module.
Just import bake_o_matic AT THE BOTTOM OF THE SCRIPT to turn it into a baker-dispatched command.
This turns any function not starting with underscore into a baker command.

This basically reduces baker boilerplate:
    import baker
    @baker.command
    def foo():
      ... 
    baker.run()
to:
    import bake_o_matic

"""
import sys
import types
# import modulefinder as mofi
import baker

main_mod=sys.modules['__main__']
public_functions=[ 
    thing for name,thing in main_mod.__dict__.items()
    if not name.startswith('_') 
    and isinstance(thing, types.FunctionType)
    ]

for func in public_functions:
    baker.command(func)

baker.run()

