"""
    IPKISS Manager CL - Command Line
    This module provides a command line interface to IPKISS Manager
"""
import os
import sys
import argparse

from ipkiss_manager.utils import ManagerSetup, parse_version
from ipkiss_manager.manager import Manager
from ipkiss_manager.im_exception import *


def create_arg_parser():
    """
        Create command line arguments parser for IPIKISS manager
    """

    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest='command')

    parse_available = sub.add_parser("list", help="List all IPKISS releases available for install.")#
    parse_installed = sub.add_parser("installed", help="List all IPKISS releases installed.")#
    parse_info = sub.add_parser("info", help="Show informations about the default IPKISS release installed.")#

    parse_set_default = sub.add_parser("set-default", help="Set a IPKISS installation as default")
    parse_set_default.add_argument("path", nargs="?", help="Path of the IPKISS that will be made as default.")
    parse_set_default.add_argument("-v", "--version", nargs="?", default="newest", help="IPKISS version. By default is assumed the newest version installed.")
    parse_set_default.add_argument("-r", "--release", nargs="?", default="ce", help="IPKISS release. Default is the Community Edition")

    parse_install = sub.add_parser("install", help="Install a version of IPKISS")
    parse_install.add_argument("version", nargs="?", default="newest", help="Which IPKISS version to install. By default install the most recent stable version")
    parse_install.add_argument("path", nargs="?", default=".", help="Path where IPKISS code will be installed.")
    parse_install.add_argument("-r", "--release", default="ce", help="Which IPKISS release to install. By default it will install the Community Edition release")

    # parse_dependency = sub.add_parser("dependency", help="Install IPKISS missing dependencies for the default ipkiss.")

    parse_remove = sub.add_parser("remove", help="Remove a version of IPKISS")
    parse_remove.add_argument("path", nargs="?", default=".", help="IPKISS code path.")
    parse_remove.add_argument("-v", "--version", nargs="?", help="IPKISS version to remove.")
    parse_remove.add_argument("-r", "--release", default="ce", help="IPKISS release. Default is the Community Edition release")

    # parse_status = sub.add_parser("status", help="Check for updates.")
    # parse_status.add_argument("path", nargs="?", default=None)

    parse_update = sub.add_parser("update", help="Update IPKISS")
    parse_update.add_argument("path", nargs="?", default=None)
    parse_update.add_argument("-v", "--version", nargs="?", default='newest')
    parse_update.add_argument("-r", "--release", nargs="?", default='ce')

    # parse_dep = sub.add_parser("dependencies", help="Install IPKISS dependencies.")
    # parse_dep.add_argument("path", nargs="?", default=None)

    parse_mv = sub.add_parser("mv", help="Move a IPKISS folder.")
    parse_mv.add_argument("orig", help="Origin")
    parse_mv.add_argument("dest", help="Destination")

    parse_scan = sub.add_parser("scan", help="Scan for removed IPKISS installations.")

    return parser


class CommandLineInterface(object):
    """
        Handle the Manager object according to the command line input
        provided by the user.
    """

    def __init__(self):
        self.manager = Manager()

    def run(self, args):
        "Receive a parsed arguments list and interpret it"

        args = args.__dict__

        func_name = 'command_%s' % args['command']
        func_name = func_name.replace('-','_')
        func = getattr(self, func_name)
        func(args)

    def _fix_distribution(self, dist, opt):
        raise NotImplemented

    def command_scan(self, args):

        corr = self.manager.scan_for_errors()

        if corr:
            for d in corr:
                v = d['version']
                r = d['release']
                uri = d['repository_uri']
                path = d['path']
                
                opt = raw_input("Distribution IPKISS {}-{} not found at path '{}'. How do you want to proceed?\n 1 - Remove this distribution\n 2 - Download this distribution again from '{}'\n 3 - set new path\n[4]- Do nothing\n->".format(v,r,uri,path))
                
                print

                if opt in ('1', '2', '3'):
                    self._fix_distribution(d, opt)

        else:
            print "No errors were found."


    def command_mv(self, args):

        try:
            orig, dest = args['orig'], args['dest']
            orig = os.path.realpath(orig)
            dest = os.path.realpath(dest)
            self.manager.mv(orig, dest)

        except UnkowIpkissRelease:
            print >>sys.stderr, "It was not possible to find an IPKISS distribution at '{}'".format(orig)

        except IOError:
            print >>sys.stderr, "It was not possible to move IPKISS distribution from '{}'' to '{}'".format(orig, dest)

    def command_dependency(self, args):

        dependency_list = self.manager.default_ipkiss['dependencies']
        install_dependency(dependency_list=dependency_list, posix_safe=True)

    def command_remove(self, args):


        if args['version'] is None:
            #remove by path
            path = args['path']

            r = raw_input("Do you really want to remove IPKISS at {}? [y,N]".format(path))
            if r.upper() != 'Y':
                return

            try:
                self.manager.remove_by_path(path=path)
            except RemoveByPathError, e:
                print >>sys.stderr, "Error removing IPKISS at {}: {}".format(path, e)

        else:
            #remove by version and release
            version, release = parse_version(args['version'], args['release'])


            r = raw_input("Do you really want to remove IPKISS {}-{}? [y,N]".format(version, release))
            if r.upper() != 'Y':
                return

            try:
                self.manager.remove_by_version(version=version, release=release)
            except RemoveByVersionError, e:
                print >>sys.stderr, "Error removing IPKISS {}-{}: {}".format(version, release, e)

    def command_list(self, args):

        releases = self.manager.available_ipkiss_releases()

        if releases:
            for r in releases:
                print "IPKISS {}-{}".format(r['version'], r['release'])
                print "\tversion:\t{}".format(r['version'])
                print "\trelease:\t{}".format(r['release'])
                print "\trepository:\t{}".format(r['repository_uri'])
                print

        else:
            print "There is any IPKISS release available at this momment"

    def command_installed(self, args):

        installed = self.manager.list_installed_ipkiss()

        if installed:
            for v in installed:

                default = ''
                if v['path'] == self.manager.default_ipkiss['path']:
                    default = '*'

                print "{}IPKISS {}-{}".format(default,v['version'], v['release'])
                print "\tversion:\t{}".format(v['version'])
                print "\trelease:\t{}".format(v['release'])
                print "\tpath:\t{}".format(v['path'])
                print "\trepository:\t{}".format(v['repository_uri'])
                print
        else:
            print "IPKISS Manager could not find an installed IPKISS release."

    def command_info(self, args):
        default_ipkiss = self.manager.default_ipkiss

        if not default_ipkiss:
            print "You don't have a default IPKISS installation."
            return

        v = [r for r in self.manager.list_installed_ipkiss() if r['path'] == default_ipkiss['path']][0]
        print "Default: IPKISS {}-{}".format(v['version'], v['release'])
        print "\tversion:\t{}".format(v['version'])
        print "\trelease:\t{}".format(v['release'])
        print "\tpath:\t{}".format(v['path'])
        print "\trepository:\t{}".format(v['repository_uri'])
        print

    def command_set_default(self, args):

        path=args["path"]
        
        version, release = parse_version(args['version'], args['release'])

        self.manager.set_default_release(path=path,
                                         version=version,
                                         release=release)

    def command_install(self, args):

        r = '?'
        while r.upper() not in ('Y','N', ''):
            print "This task may take a long time, do you want to proceed anyway? [Y,n]",
            r = raw_input()
            if r.upper() == 'N':
                return

        version, release = parse_version(args['version'], args['release'])

        if version == "newest":
            try:
                self.manager.install_latest_version(path=args['path'], console=True) #release CE
            except VersionError:
                print >>sys.stderr, "It was not possible to install IPKISS at {}".format(args["path"])

        else:
            try:
                self.manager.install_ipkiss(version=version, path=args['path'], console=True) #release CE
            except VersionError:
                print >>sys.stderr, "It was not possible to find version {}".format(args["version"])


    def command_update(self, args):

        if args['path']:
            self.manager.update_ipkiss(path=args['path'])

        else:
            # update ipkiss in use
            version, release = parse_version(args['version'], args['release'])
            self.manager.update_ipkiss(version=version, release=release)


def setup():
    s = ManagerSetup()
    todo = s.todo_list()

    if not todo:
        # there is nothing to do, go away...
        return

    print "IPKISS Manager must execute setup scripts before continue. Do you want to continue with setup? [y,N]",
    response = raw_input()

    if response.upper() == 'Y':
        print "IPKISS Manager will run the setup scripts. It must take few minutes."
        s.set_it_up()
    else:
        exit(1)


def main():

    setup()

    arg_parser = create_arg_parser()
    parsed_arguments = arg_parser.parse_args()
    cli = CommandLineInterface()
    cli.run(parsed_arguments)

if __name__ == '__main__':
    main()

