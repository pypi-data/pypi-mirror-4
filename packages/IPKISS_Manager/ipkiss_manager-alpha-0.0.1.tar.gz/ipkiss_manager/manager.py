
from __init__ import LOCAL_DATA_FOLDER

import urllib2
import json
import os
import shutil
import utils
import pyhg

from im_exception import *


class RefManager(object):
    """
        The RefManager object manages only the references.
        It will AWAYS check the reference file served by IPKISS website

        local_references: contains references about your local IPKISS installation
        external_references: contains references of all available IPKISS version (online available)

        for informations about reference files see: references.rst
    """

    def __init__(self, reference_folder=LOCAL_DATA_FOLDER):

        self.reference_folder = reference_folder

        try:
            self.local_references = json.load( open(os.path.join(reference_folder, 'local_references.json')) )
        except IOError:
            raise ReferenceFileError("It was not possible to find a local reference file.")

        reference_file = os.path.join(reference_folder, 'external_references.json')

        if os.path.isfile(reference_file):
            with open(reference_file,'r') as ref:
                backup_reference = json.load(ref)
        else:
            backup = None

        try:
            updated_references = self.get_online_references()
            with open(reference_file,'w') as ref:
                ref.write(json.dumps(updated_references))

            self.external_references = updated_references

        except TimeoutError:
            if backup_reference:
                self.external_references = backup_reference
            else:
                raise UnsolvableError("No local reference nor online reference available.")

    def get_online_references(self):
        """
            Check for a new reference file
        """

        references_uri = self.local_references['reference_server']

        count = 0
        while True:
            try:
                response = urllib2.urlopen(references_uri)
                return json.loads(response.read())
            except urllib2.HTTPError:
                pass
            else:
                break
            count += 1
            if count > 20:
                raise TimeoutError("It was not possible to found an online reference file.")

    def _update_local_references(self):
        """ Copy self.local_references to the file at fixtures folder """

        ref_file = os.path.join(self.reference_folder, 'local_references.json')

        # first backup old file
        if os.path.isfile(ref_file):
            shutil.copy(ref_file, ref_file+'.backup')

        # than save new file
        with open(ref_file, 'w') as ref:
            ref.write(json.dumps(self.local_references))

    def update_reference(self, **kwargs):
        """
            change local_references content AND change it on reference file
        """

        _local_references = self.local_references.copy()

        for key in kwargs:
            _local_references[key] = kwargs[key]

        self.local_references = _local_references
        self._update_local_references()


class Manager(object):

    def __init__(self, path=LOCAL_DATA_FOLDER):

        if not self.dependency_free():
            raise DependencyError()

        self.ref_manager = RefManager(path)
        self.default_ipkiss = self.ref_manager.local_references['in_use_ipkiss']

    def get_default_release(self):
        return ''

    def dependency_free(self):
        """ Check if the manager has all the necessary dependencies to work """
        try:
            import mercurial
        except:
            return False

        return True

    def available_ipkiss_releases(self):
        return self.ref_manager.external_references['releases']

    def manageable_repository(self, path):

        metadata_file = os.path.join(path, ".metadata.json")

        try:
            mf = open(metadata_file, "r")
            metadata = json.load(mf)
            metadata['version']
            metadata['release']
            metadata['repository_uri']

        except (IOError, KeyError):
            return False

        return True

    def list_installed_ipkiss(self):
        return self.ref_manager.local_references['installed_distributions']

    def set_current_ipkiss(self, version, release='ce'):
        """ Set the current INSTALLED ipkiss version managed by the app """
        pass

    @classmethod
    def compare_versions(cls, a, b):
        """
            gets a and b and return the greater one
        """
        _a = a.split('.')
        _b = b.split('.')
        for (i,j) in zip(a,b):
            if i > j:
                return a
            elif j > i:
                return b
        return a

    def get_latest_version(self):
        versions = [r['version'] for r in self.ref_manager.external_references['releases'] if r['release'] == 'ce']
        return reduce(lambda a,b : self.compare_versions(a,b), versions)

    def get_latest_installed_version(self):
        versions = [r['version'] for r in self.ref_manager.local_references['installed_distributions'] if r['release'] == 'ce']
        return reduce(lambda a,b : self.compare_versions(a,b), versions)

    def install_latest_version(self, path, console=False):
        version = self.get_latest_version()
        self.install_ipkiss(path, version, console=console)

    def install_ipkiss(self, path, version, release="ce", console=False):

        for rel in self.ref_manager.external_references['releases']:

            if rel['version'] == version and rel['release'] == release:

                uri = rel['repository_uri']
                dependencies = rel['dependencies']

                if console:
                    print "Installing dependencies"
                self._install_dependencies(dependencies)

                if console:
                    print "Cloning repository from '{}'. It may take a couple of minutes.".format(uri)
                self._install_ipkiss(path, uri, version, release, dependencies)

                break

        else:
            #it was not possible to find this version/release.
            #How to handle this?
            raise VersionError("version '{}' unknow".format(version)) #TODO: create a proper exception

    def _install_dependencies(self, dependency_list):
        utils.install_dependencies(dependency_list)

    def _install_ipkiss(self, path, repository_uri, version, release, dependencies):

        repo = pyhg.Repo(path)
        folder_name = 'ipkiss{}-{}'.format(version, release)
        path = os.path.realpath(os.path.join(path, folder_name))
        repo.hg_clone(repository_uri, dest=folder_name)

        metadata = {"version":version,
                    "release":release,
                    "repository_uri":repository_uri,
                    "path":path,
                    "dependencies":dependencies,
                    }

        metadata_file = os.path.join(path, ".metadata.json")
        with open(metadata_file, "w") as mf:
            json.dump(metadata, mf)

        installed_distributions = self.ref_manager.local_references['installed_distributions'][:]
        installed_distributions.append(metadata)
        self.ref_manager.update_reference(in_use_ipkiss=metadata, installed_distributions=installed_distributions)

    def update_ipkiss(self):
        """ update the current ipkiss version"""
        pass

    def upgrade_ipkiss(self, new_version):
        raise NotImplemented("Upgrade system is not yet available")

    def remove_by_path(self, path):

        path = os.path.realpath(path)
        installed_distributions = self.ref_manager.local_references['installed_distributions'][:]
        if path in [p['path'] for p in installed_distributions]:
            installed_distributions = [p for p in installed_distributions if p['path'] != path]

            try:
                shutil.rmtree(path)
            except OSError:
                raise RemoveByPathError('It was not possible to remove IPKISS from "{}": Permission denied or already removed folder.'.format(path))

            self.ref_manager.update_reference(installed_distributions=installed_distributions[:])

        else:
            raise RemoveByPathError('It was not possible to remove IPKISS from "{}": Path not managed by IPKISS Manager'.format(path))

        # if removing default release, handle it:
        if self.default_ipkiss and self.default_ipkiss['path'] == path:
            self.default_ipkiss = ""
            self.ref_manager.update_reference(in_use_ipkiss="")

    def remove_by_version(self, version, release):

        installed_distributions = self.ref_manager.local_references['installed_distributions'][:]

        if (version, release) in [(d['version'], d['release']) for d in installed_distributions]:
            to_delete =  [d for d in installed_distributions if d['version'] == version and d['release'] == release ][0]

            path = to_delete['path']

            installed_distributions = installed_distributions[:]
            installed_distributions.remove(to_delete)

            try:
                shutil.rmtree(path)
            except OSError:
                raise RemoveByPathError('It was not possible to remove IPKISS from "{}": Permission denied or already removed folder.'.format(path))

            self.ref_manager.update_reference(installed_distributions=installed_distributions[:])

            # if removing default release, handle it:
            if self.default_ipkiss and self.default_ipkiss['path'] == path:
                self.default_ipkiss = ""
                self.ref_manager.update_reference(in_use_ipkiss="")

        else:
            raise RemoveByPathError('It was not possible to remove IPKISS {}-{}: Version not managed by IPKISS Manager'.format(version, release))

    def set_default_release(self, path=None, version=None, release=None):

        if path is None:
            # get path from installed list
            if version == 'newest':
                version = self.get_latest_installed_version()

            installed_dist = self.ref_manager.local_references['installed_distributions']
            installed_dist = filter(lambda dist : dist['version'] == version and dist ['release'] == release, installed_dist)

            if not installed_dist:
                raise UnkowIpkissRelease("It was not possible to find IPKISS {}-{}'".format(version, release))

            path = installed_dist[0]['path']

        # now set by path
        try:
            with open( os.path.join(path, '.metadata.json'), 'r') as metadata_file:
                metadata = json.load(metadata_file)
                self.default_ipkiss=metadata.copy()
                self.ref_manager.update_reference(in_use_ipkiss=metadata.copy())
                #TODO: put metadata['path'] in pythonpath

        except IOError:
            raise UnkowIpkissRelease("It was not possible to find a metadata file at '{}'".format(path))

    def update_ipkiss(self, path=None, version=None, release=None):
        
        if path is None:
         # get path from installed list
            if version == 'newest':
                version = self.get_latest_installed_version()

            installed_dist = self.ref_manager.local_references['installed_distributions']
            installed_dist = filter(lambda dist : dist['version'] == version and dist['release'] == release, installed_dist)

            if not installed_dist:
                raise UnkowIpkissRelease("It was not possible to find IPKISS {}-{}'".format(version, release))

            path = installed_dist[0]['path']
            uri = installed_dist[0]['repository_uri']

        repo = pyhg.Repo(path)
        repo.hg_pull()
        repo.hg_update("tip")


    def mv(self, orig, dest):
        metadata_file = os.path.join(orig, '.metadata.json' )
        try:
            open(metadata_file)
        except IOError:
            raise UnkowIpkissRelease()

        shutil.move(orig, dest)# can raise IOERROR

        #update metadata
        metadata_file =  open(os.path.join(dest, '.metadata.json'))
        metadata = json.load(metadata_file)
        metadata['path'] = os.path.realpath(dest)
        metadata_file.close()

        metadata_file =  open(os.path.join(dest, '.metadata.json'), 'w')
        json.dump(metadata, metadata_file)
        metadata_file.close()

        #update local_references
        dist = self.ref_manager.local_references['installed_distributions'][:]
        dist = [d for d in dist if d['path'] != orig] + [metadata]
        self.ref_manager.update_reference(installed_distributions=dist)

        # if moving default release, handle it:
        if self.default_ipkiss and self.default_ipkiss['path'] == orig:
            self.set_default_release(path=dest)

    def scan_for_errors(self):

        corrupt = []
        dist = self.ref_manager.local_references['installed_distributions']

        for d in dist:
            try:
                metadata_file = os.path.join(d['path'], '.metadata.json' )
                open(metadata_file)

            except IOError:
                # There is no metadata file
                corrupt.append(d.copy())

        return corrupt
