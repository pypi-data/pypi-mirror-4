"""
This module redefines the global help() function.  If the 'thing'
being requested for help has the '__help__' attribute, then that
string is used to provide help information.  Otherwise, the standard
help utility is used.
"""

old_help = help

def help(thing=None):                               #pragma:nocover
    if not thing is None and hasattr(thing, '__help__'):
        print(thing.__help__)
    else:
        old_help(thing)

try:
    __builtins__['help'] = help
except:                                             #pragma:nocover
    # If this fails, then just die silently.
    pass
