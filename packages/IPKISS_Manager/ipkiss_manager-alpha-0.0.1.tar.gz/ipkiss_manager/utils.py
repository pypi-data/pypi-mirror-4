import os
import shutil
import urllib2
import subprocess

from setuptools.command import easy_install

from __init__ import FIXTURES, LOCAL_DATA_FOLDER
from im_exception import *


DEPENDENCY_WEBSITE = 'http://www.ipkiss.org/dependencies'


def parse_version(version, release=None):
    """
        input: 2.3, 2.3-ce, 2.3-CE ...
        output: tuple(version, release)
    """
    if '-' in version:
        v,r = version.split('-')

    else:
        v,r = version, None
    
    r = r or release

    return (v,r)

def download_it(url, file_name, data_folder=LOCAL_DATA_FOLDER):

    """
    Dowload a file given by the url
    download_it returns an iterator that must be consumed to finish the download process!
    """

    file_name = os.path.join(data_folder, file_name)

    if not isinstance(url,basestring):
        raise TypeError("'url' must be a string not %s" % type(url))

    if not isinstance(file_name,basestring):
        raise TypeError("'file_name' must be a string not %s" % type(file_name))

    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()

    if not meta.getheaders("Content-Length"):
        #TODO: implement logging!
        raise DownloadError("It was not possible to download '%s'" % url)

    file_size = int(meta.getheaders("Content-Length")[0])

    file_size_dl = 0
    block_sz = 8192
    while True:
        buff = u.read(block_sz)
        if not buff:
            break

        file_size_dl += len(buff)
        f.write(buff)

        yield (file_size_dl, file_size)

    f.close()


def download_full(url, file_name, data_folder=LOCAL_DATA_FOLDER):
    """
    An example to use download_it
    """
    for i in download_it(url, file_name, data_folder):
        print i


def check_dependency(dependencies):

    """Return a list of dependencies that are not working"""

    dep = []
    for d in dependencies:
        try:
            exec('import %s' % d)
        except ImportError, e:
            dep.append(d)

    return dep


def check_hard_dependencies():

    """Check for numpy and scipy dependencies"""

    hard_requires = []

    try:
        import numpy
    except ImportError:
        hard_requires.append('numpy')

    try:
        import scipy
    except ImportError:
        hard_requires.append('scipy')

    return hard_requires


def postpone_hard_dependencies():
    import Tkinter
    import tkMessageBox

    message = "You must have Numpy and Scipy installed to run IPKISS.\n\nYou can proceed the installation without those dependencies and install it latter or cancel the installation untill you have it properly installed.\n\nDo you want to proceed with the installation?\n\n(For further informations see %s)\n" % DEPENDENCY_WEBSITE

    return tkMessageBox.askokcancel('Proceed anyway?',message)


def setup_references_folder():

    """ Create data folder (if it doesn't exist) and save initial reference file """

    if not os.path.isdir(LOCAL_DATA_FOLDER):

        # new installation, create new ref. file
        os.mkdir(LOCAL_DATA_FOLDER)
        f = os.path.join(FIXTURES, 'local_references.json')
        name = os.path.join(LOCAL_DATA_FOLDER, 'local_references.json')
        shutil.copyfile(f, name)

    else:
        # just updating software, do not create new file
        # call here update scripts, when it exists
        pass


def install_dependencies(dependency_list, posix_safe=False):
    """ dependency_list must follow the schema: ["lib_name", "distribution_name), ...] """

    if os.name == 'nt' or posix_safe:

        for (lib, pack) in dependency_list:
            try:
                exec("import %s" % lib)
            except ImportError:
                easy_install.main(["-U", pack])


class ManagerSetup(object):
    """
        This class wraps a bunch of setup code that must be executed at the
        first time on running IPKISS_manager.
    """

    def _shapely_works(self):
        "return True or False if shapely is working"
        try:
            import shapely

            if os.name == 'posix':
                return True
            else: #windows
                return not bool( os.system('python -c "from shapely.geometry import Polygon"') )

        except:
            return False

    def _download_and_install_shapely(self):
        """
            Download a .exe installer for shapely. Useful when nothing else works
        """
        from manager import RefManager

        r = RefManager()
        uri = r.external_references['shapely_bin']
        download_full(uri, 'shapely_binary.exe')
        subprocess.call( [os.path.join(LOCAL_DATA_FOLDER, 'shapely_binary.exe')]  )

    def _remove_shapely(self):
        """
            Remove current version of shapely installed
        """
        try:
            import shapely
        except ImportError:
            return
        path = os.path.dirname(shapely.__file__)

        if path.endswith('shapely'):
            shutil.rmtree(path)

    def _install_shapely(self):
        """shapely is a quite complicated dependency, so this script manages to install it"""

        if not self._shapely_works():

            if os.name == 'posix':
                easy_install.main(["-U", 'shapely'])

            else: # windows
                self._remove_shapely() #remove old shapely installation, if it exists
                try:
                    self._download_and_install_shapely()
                except Exception, e:
                    raise ShapelyNotInstalled("It was not possible to install Shapely." + e)
                if not self._shapely_works():
                    raise ShapelyNotInstalled("Shapely was installed, but it doesn't work properly.")

    def set_it_up(self):
        """
            Setup IPKISS_manager
        """
        setup_references_folder()
        if os.name == 'nt':
            install_dependencies([["mercurial","purehg"],])
            self._install_shapely()

    def todo_list(self):
        """
            Just let you know what has to be setted up
        """

        to_do = []

        if not os.path.isdir(LOCAL_DATA_FOLDER):
            to_do.append('data_folder')

        if not self._shapely_works():
            to_do.append('shapely')

        try:
            import mercurial
        except ImportError:
            to_do.append('mercurial')

        return to_do
