
import argparse
import coopr_parser
import os
import os.path
import sys
import glob
import datetime
#import textwrap
import pyutilib.subprocess

def setup_command_parser(parser):
    parser.add_argument("--list", dest="summary", action='store_true', default=False,
                        help="list the active solvers")
    parser.add_argument("command", nargs='*', help="The command and command-line options")

def command_exec(options):
    cmddir = os.path.dirname(os.path.abspath(sys.executable))+os.sep
    if options.summary:
        print("")
        print("The following commands are installed in the Coopr bin directory:")
        print("----------------------------------------------------------------")
        for file in glob.glob(cmddir+'*'):
            print("", os.path.basename(file))
        print("")
        if len(options.command) > 0:
            print("WARNING: ignoring command specification")
        return
    if len(options.command) == 0:
        print("ERROR: no command specified")
        return
    if not os.path.exists(cmddir+options.command[0]):
        print("ERROR: the command '%s' does not exist" % (cmddir+options.command[0]))
        return
    pyutilib.subprocess.run(cmddir+' '.join(options.command), tee=True)

def version_exec(options):
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('coopr').version
    except:
        import coopr.coopr
        version = coopr.coopr.version
    print("Coopr version "+version)

def setup_api_parser(parser):
    parser.add_argument("-a", "--asciidoc", dest="asciidoc", action='store_true', default=False,
                        help="Output the API summary using ASCIIDOC syntax")

def api_exec(options):
    import coopr.core
    services = coopr.core.CooprAPIFactory.services()
    #
    f = {}
    for name in services:
        f[name] = coopr.core.CooprAPIFactory(name)
    #
    ns = {}
    for name in services:
        ns_set = ns.setdefault(f[name].__namespace__, set())
        ns_set.add(name)
    #
    if options.asciidoc:
        print("//")
        print("// Coopr Library API Documentation")
        print("//")
        print("// Generated with 'coopr api' on ",datetime.date.today())
        print("//")
        print("")
        print("== Coopr Functor API ==")
        for ns_ in sorted(ns.keys()):
            print("")
            level = ns_+" Functors"
            print('=== %s ===' % level)
            for name in sorted(ns[ns_]):
                if ns_ != '':
                    tname = name[len(ns_)+1:]
                else:
                    tname = name
                print("")
                print('==== %s ====' % tname)
                print(f[name].__short_doc__)
                if f[name].__long_doc__ != '':
                    print("")
                    print(f[name].__long_doc__)
                print("")
                flag=False
                print("- [underline]#Required Keyword Arguments:#")
                for port in sorted(f[name].inputs):
                    if f[name].inputs[port].optional:
                        flag=True
                        continue
                    print("")
                    print('*%s*::\n %s' % (port, f[name].inputs[port].doc))
                if flag:
                    # A function may not have optional arguments
                    print("")
                    print("- [underline]#Optional Keyword Arguments:#")
                    for port in sorted(f[name].inputs):
                        if not f[name].inputs[port].optional:
                            continue
                        print("")
                        print('*%s*::\n %s' % (port, f[name].inputs[port].doc))
                print("")
                print("- [underline]#Return Values:#")
                for port in sorted(f[name].outputs):
                    print("")
                    print('*%s*::\n %s' % (port, f[name].outputs[port].doc))
                print("")
    else:
        print("=================")
        print("Coopr Functor API")
        print("=================")
        for ns_ in sorted(ns.keys()):
            print("")
            level = ns_+" Functors"
            print("-"*len(level))
            print(level)
            print("-"*len(level))
            for name in sorted(ns[ns_]):
                if ns_ != '':
                    tname = name[len(ns_)+1:]
                else:
                    tname = name
                print(tname+':')
                for line in f[name].__short_doc__.split('\n'):
                    print("    "+line)

#
# Add a subparser for the coopr command
#
setup_command_parser(
    coopr_parser.add_subparser('run',
        func=command_exec, 
        help='Execute a command from the Coopr bin (or Scripts) directory.',
        description='This coopr subcommand is used to execute commands installed with Coopr.',
        epilog="""
This subcommand can execute any command from the bin (or Script)
directory that is created when Coopr is installed.  Note that this
includes any commands that are installed by other Python packages
that are installed with Coopr.  Thus, if Coopr is installed in the
Python system directories, then this command executes any command
included with Python.
"""
        ))

coopr_parser.add_subparser('version',
        func=version_exec, 
        help='Print the Coopr version.',
        description='This coopr subcommand is used to print the version of the Coopr release.')

setup_api_parser(
coopr_parser.add_subparser('api',
        func=api_exec, 
        help='Print information about the Coopr Library API.',
        description='This coopr subcommand is used to print a summary of the Coopr Library API.'))

def main(args=None):
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    parser.set_defaults(func=main_exec)
    ret = parser.parse_args(args)
    ret = ret.func(ret)

