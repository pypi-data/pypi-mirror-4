#!/usr/bin/env python

"""
Example of usage python module for NooLite USB stick

Last version at: https://github.com/Sicness/pyNooLite
"""
import sys
import noolite

__author__ = "Anton Balashov"
__license__ = "GPL v3"
__maintainer__ = "Anton Balashov"
__email__ = "Sicness@darklogic.ru"

def help():
    print """
    Example of usage NooLite class

    USAGE:
    on <ch>     Turn power on on channel
    off <ch>    Turn power off on channel
    switch <ch> Switch between on and off on channel
    set <ch> <lvl>  Set power level on channel
    bind <ch>   Send bind signal on channel
    unbind <ch> Send unbind signal on channel

    channales should be in 0-7
    level should be in 0-120

    Examples:
        $ python main.py on 1
        $ python main.py set 0 115
    """

if __name__ == '__main__':
    if len(sys.argv) < 3:
        help()
        sys.exit(0)

    cmd = sys.argv[1]
    ch = sys.argv[2]
    if cmd == 'set':
        if len(sys.argv) == 4:
            lvl = int(sys.argv[3])
        else:
            sys.stderr.write("command 'set' must have additional agument 'lvl'")
            help()
            sys.exit(1)

    n = noolite.NooLite()
    cmds = {'on' : n.on,
        'off': n.off,
        'switch': n.switch,
        'set': n.set,
        'bind': n.bind,
        'unbind': n.unbind}

    if not cmd in cmds:
        sys.stderr.write("Unknow command %s\n" % (cmd))
        help()
        sys.exit(4)

    try:
        if sys.argv[1] == 'set':
            cmds[cmd](ch, lvl)
        else:
            cmds[cmd](ch)
    except (ValueError, noolite.NooLiteErr) as e:
        sys.stderr.write(str(e))
        sys.exit(3)
