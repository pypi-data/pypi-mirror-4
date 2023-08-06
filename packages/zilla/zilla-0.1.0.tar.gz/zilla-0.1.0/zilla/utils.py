import sys

def usage():
    print """
usage: zilla COMMAND [OPTIONS]

TODO
""".strip()
    sys.exit(1)

def command_importer(subcmd):
    try:
        mod = __import__("zilla.commands.%s" % subcmd)
        subcmd = "zilla.commands." + subcmd
    except ImportError:
        try:
            mod = __import__("zilla_%s" %subcmd)
        except ImportError:
            print "Unknown command '%s'" % subcmd
            print
            usage()

    components = subcmd.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod
