#!/usr/bin/env python
# -*- coding: utf-8 -*-

# all names not starting with under score must be a subcommand module.
import jsonstream as jsons
import tsv
import io
# import util
import graph
import dbi
import panya

def _main():
    
    panya.panya.register()

    panya.panya.baker.run()

