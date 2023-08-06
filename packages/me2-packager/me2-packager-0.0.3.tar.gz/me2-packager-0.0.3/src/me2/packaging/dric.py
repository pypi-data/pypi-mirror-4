'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import os
import netrc
import logging
import urllib2
import hashlib
import lockfile
import tempfile
import shutil

from webdav import WebdavClient

class PasswordManager(object):
    log = logging.getLogger("PasswordManager")

    def __init__(self):
        self.credentials = {}
        self.credentials.update(self.load_netrc())

    def load_netrc(self):
        try:
            n = netrc.netrc()
            cred = n.hosts
        except IOError:
            self.log.error("Could not load .netrc file. Skipping")
            cred = {}
        return cred

    def get_login(self, hostname):
        return self.credentials.get(hostname, None)

    def get_login_by_url(self, url):
        parsed_url = urllib2.urlparse.urlparse(url)
        return self.get_login(parsed_url.hostname)

class DownloadError(Exception): pass

class Downloader(object):
    """This class downloads files to the cache_dir and allows you to copy them to specified locations
    """
    log = logging.getLogger("Downloader")
    def __init__(self, cache_dir = None, block_size = 1024):
        self.block_size = block_size

        self.password_manager = PasswordManager()

        if cache_dir is None:
            self.cache_dir = os.path.join(os.path.expanduser("~"), ".m2pack", "cache")
        else:
            self.cache_dir = cache_dir

        if not os.path.exists(self.cache_dir):
            self.log.debug("Creating cache dir: %s", self.cache_dir)
            os.makedirs(self.cache_dir)
        self.log.info("Using cache dir: %s", self.cache_dir)

    def _generate_url_identifier(self, url_string):
        m = hashlib.md5()
        m.update(url_string)
        return m.hexdigest()

    def download(self, url_string, fname = None, credentials = None):
        self.log.debug("Starting download for: %s", url_string)
        urllib_password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        url = urllib2.urlparse.urlparse(url_string)

        #ToDo: Should we add all credentials from .netrc to the database ?!
        if credentials is None:
            self.log.info("Checking stored credentials")
            cred = self.password_manager.get_login(url.hostname)
            if cred is not None:
                username = cred[0]
                password = cred[2]
                credentials = (username, password)
                self.log.info("Using stored credentials for server %s (username = %s)", url.hostname, username)

        if credentials is not None:
            username = credentials[0]
            password = credentials[1]
            urllib_password_manager.add_password(None, url_string, username, password)

        self.log.info("Registering Password manager")
        handler = urllib2.HTTPBasicAuthHandler(urllib_password_manager)
        opener = urllib2.build_opener(handler)
        try:
            remote_object = opener.open(url_string)
        except urllib2.HTTPError, e:
            self.log.exception("Failed to download: %s", url_string)
            raise DownloadError(e)
        effective_url_string = remote_object.geturl()
        effective_url = urllib2.urlparse.urlparse(effective_url_string)

        if fname is None:
            fname = os.path.basename(effective_url.path)
            self.log.debug("No destination filename specified. Determined one is: %s", fname)

        destination_dir = os.path.join(self.cache_dir, self._generate_url_identifier(effective_url_string))
        self.log.debug("Destination directory is: %s", destination_dir)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        destination_file = os.path.join(destination_dir, fname)
        self.log.debug("Effective destination file is: %s", destination_file)
        if os.path.exists(destination_file):
            self.log.info("File already downloaded.")
            return destination_file

        flock = lockfile.FileLock(destination_file)

        temp_file = tempfile.NamedTemporaryFile(dir = destination_dir, prefix = "%s.tmp." % fname, delete = False)
        ok = False
        try:
            self.log.debug("Acquireing lock")
            flock.acquire()
            with temp_file:
                self.log.info("Reading remote file")
                while True:
                    block = remote_object.read(self.block_size)
                    if len(block) <= 0:
                        break
                    temp_file.write(block)
            ok = True
            remote_object.close()
        finally:
            self.log.debug("Releasing log")
            flock.release()
            if ok:
                os.rename(temp_file.name, destination_file)
            else:
                os.remove(temp_file.name)
        if ok:
            self.log.info("File downloaded successfuly")
            return destination_file
        else:
            self.log.warn("Failed to download file")

    def fetch(self, url_string, destination_file, source_file = None):
        cache_file = self.download(url_string)
        if cache_file is None:
            raise # ToDo: raise a custom exception
        shutil.copyfile(cache_file, destination_file)

class Uploader(object):
    log = logging.getLogger("Uploader")
    def __init__(self, default_remote_location):
        self.default_server = default_remote_location

    def upload(self, local_file, remote_location = None):
        if remote_location is None:
            remote_location = self

class RepositoryError(Exception): pass
class RepositoryCouldNotDownload(RepositoryError):pass

class Repository(object):
    password_manager = PasswordManager()
    downloader = Downloader()

    def __init__(self, name, repository):
        self.log = logging.getLogger("Repository-%s" % name)
        self.repository = repository
        self.log.debug("URL: %s", repository)

    def fetch_file(self, groupId, artifactId, version, classifier):
        url = self.__generate_url(self.repository, groupId, artifactId)
        if not url.endswith("/"):
            url += "/"
        url = "%s%s" % (url, self.__generate_file_name(artifactId, version, classifier))
        try:
            local_file = self.downloader.download(url)
        except DownloadError, e:
            self.log.exception("Could not download file")
            raise RepositoryCouldNotDownload(e)
        if local_file is None:
            self.log.critical("Failed to download file %s", url)
            raise RepositoryCouldNotDownload("Could not download: %s" % url)
        return local_file

    def fetch(self, groupId, artifactId, version, classifier):
        local_file = self.fetch_file(groupId, artifactId, version, classifier)
        return open(local_file, "r")

    def register(self, bundle):
        if isinstance(bundle, basestring):
            raise NotImplementedError("Loading from file is not supported yet")
        local_artifact = bundle.package_file_path
        self.register_file(bundle.info.group_id, bundle.info.package_id, bundle.info.version, bundle.info.classifier, local_artifact)

    def register_file(self, groupId, artifactId, version, classifier, local_artifact, artifact_remote_file = None):
        if artifact_remote_file is None:
            artifact_remote_file = self.__generate_file_name(artifactId, version, classifier)
        url = self.__generate_url(self.repository, groupId, artifactId)
        self.log.debug("URL is: %s", url)
        resource = WebdavClient.CollectionStorer(url)
        cred = self.password_manager.get_login_by_url(url)
        if cred is not None:
            resource.connection.addBasicAuthorization(cred[0], cred[2])
        child = resource.addResource(artifact_remote_file)
        child.uploadFile(open(local_artifact, "rb"))


    def __generate_file_name(self, artifactId, version, classifier):
        return "%s-%s-%s.mb" % (artifactId, version, classifier)

    def __generate_url(self, repository, groupId, artifactId):
        group_id_path = "/".join(groupId.split("."))
        return "%(repo)s/%(group_id)s/%(artifact_id)s/" % {'repo': repository,
                                                           'group_id': group_id_path,
                                                           'artifact_id': artifactId,
                                                           }

class MetaRepository(object):
    log = logging.getLogger("MetaRepository")
    def __init__(self, repositorys = []):
        self.repositorys = []
        for repo in repositorys:
            self.repositorys.append(Repository(repo["name"], repo["url"]))

    def fetch_file(self, groupId, artifactId, version, classifier):
        ok = False
        for repo in self.repositorys:
            try:
                local_file = repo.fetch_file(groupId, artifactId, version, classifier)
            except RepositoryCouldNotDownload, e:
                self.log.exception("")
                continue
            return local_file

        if not ok:
            raise RepositoryCouldNotDownload("Could not download artifact %s:%s:%s:%s from any repository" % (groupId, artifactId, version, classifier))

    def fetch(self, groupId, artifactId, version, classifier):
        return open(self.fetch_file(groupId, artifactId, version, classifier), "r")


if __name__ == "__main__":
    logging.basicConfig(format = '[ %(levelname)-8s %(filename)s:%(lineno)d (%(name)s) ] --> %(message)s',
                        datefmt = '%d/%b/%Y %H:%M:%S',
                        level = 10)
    #fname = "/home/marian/repos/me2/me2-pack/packaging/bundles/mos-bundle/me2-build/mOS-0.5-x86.mb"
    repos = [ {"name": "dummy", "url": "http://web.info.uvt.ro/test" },
             {"name": "mosaic", "url": "http://developers.mosaic-cloud.eu/artifactory/mosaic"},
             ]
    #repo = Repository("http://developers.mosaic-cloud.eu/artifactory/mosaic")
    repo = MetaRepository(repos)
    #repo.register("ro.ieat.mosaic.bundles", "mOS", "0.5", "x86", fname)
    print repo.fetch("ro.ieat.mosaic.bundles", "mOS", "0.5", "x86")
