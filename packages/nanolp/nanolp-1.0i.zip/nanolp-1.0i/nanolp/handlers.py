# Event handlers
#
# Author: Balkansoft.BlogSpot.com
# GNU GPL licensed

import nanolp.core as core

# Inspection (reflection) does not work on native funcs., so wrap they
def lower(s): return s.lower()
def lstrip(s): return s.lstrip()
def rstrip(s): return s.rstrip()
def strip(s): return s.strip()
def swapcase(s): return s.swapcase()
def title(s): return s.title()
def upper(s): return s.upper()

core.EventHandler.register_func('lower', lower)
core.EventHandler.register_func('lstrip', lstrip)
core.EventHandler.register_func('rstrip', rstrip)
core.EventHandler.register_func('strip', strip)
core.EventHandler.register_func('swapcase', swapcase)
core.EventHandler.register_func('title', title)
core.EventHandler.register_func('upper', upper)
