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

import re
import os
import json
import pipes
import copy
import hashlib
import logging
import tarfile
import fnmatch
import zipfile
import StringIO
import glob
from tools import zip_file_buffer

from dric import Downloader, Repository

SPEC_FILE_NAME = "spec.json"
SPEC_FILE_VERSION = "0.1"

DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".me2pack")

ARTIFACT_SPECIFICATION_RE = re.compile(r"(?P<SPEC>(?P<GROUPID>\w(\w|\d|\-|_)*(\.\w(\w|\d|\-|_)*)*){1}:(?P<ARTIFACT>\w+(\w|\d|\_)*){1}:(?P<VERSION>\d+(\.|\d)*){1}(:(?P<CLASSIFIER>\w+))?)")
VARIABLE_EXPANSION_RE = re.compile(r"(?P<variable>\${(?P<path>((\w|\-)+)(\.(\w|\-)+)*)(\|(?P<transform>\w+))?})")
VARIABLE_EXPANSION_TRANSFORM_HANDLERS = {'sh': pipes.quote}

class VariableExpansionError(Exception): pass
class PropertyNotFound(VariableExpansionError): pass
class InvalidProperty(VariableExpansionError): pass
class SpecificationError(Exception): pass
class UnsupportedSpecificationError(SpecificationError): pass
class BundleError(Exception): pass
class BundleFormatError(BundleError): pass
class BundleIOError(BundleError): pass
class UnsupportedBundle(BundleError): pass
class BundleSpecError(BundleError):pass

def expand_variables(input_string, tree, default = None, panic_if_not_found = True, nesting_level = 0, max_nesting_level = 15):
    _nest_level = nesting_level
    if _nest_level > max_nesting_level:
        raise VariableExpansionError("Nesting level above configured limit %d" % max_nesting_level)
    def replace(match):

        _group_dict = match.groupdict()
        _path = _group_dict['path']
        if 'transform' in _group_dict:
            _transform = _group_dict['transform']
            if _transform is None:
                _escape = str
            else:
                if _transform not in VARIABLE_EXPANSION_TRANSFORM_HANDLERS:
                    raise VariableExpansionError("Transform `%s` not found, valid transforms: %s" % (_transform, VARIABLE_EXPANSION_TRANSFORM_HANDLERS.keys()))
                _escape = VARIABLE_EXPANSION_TRANSFORM_HANDLERS[_transform]
        else:
            _escape = str
        _obj = tree
        path_elements = _path.split(".")

        terminal = path_elements[-1]
        parents = path_elements[:-1]

        _obj = tree
        for node in parents: # Validate the parents
            if node not in _obj:
                raise PropertyNotFound("Property %s not found (%s)" % (_path, node))
            if not isinstance(_obj[node], dict): # All parent should be dict's
                raise InvalidProperty("Property %s could not be expanded. Node %s is not a dictionary !" % (_path, node))
            _obj = _obj[node]

        if terminal not in _obj:
            raise PropertyNotFound("Property %s not found" % _path)

        _obj = _obj[terminal]

        if isinstance(_obj, basestring) or isinstance(_obj, int) or isinstance(_obj, float):
            return _escape(str(_obj))
        else:
            raise InvalidProperty("Property %s is not a string" % _path)


    new_string, num_subs = VARIABLE_EXPANSION_RE.subn(replace, input_string)
    if num_subs == 0:
        return new_string
    else:
        return expand_variables(new_string, tree, default, panic_if_not_found, nesting_level + 1, max_nesting_level)

def sha1file(fname):
    m = hashlib.sha1()
    with open(fname, "rb") as f:
        while True:
            buf = f.read(512)
            if len(buf) <= 0:
                break
            m.update(buf)

    return m.hexdigest()

def validate_spec(spec):
    if "spec-version" not in spec:
        raise SpecificationError("Missing specification")
    if spec["spec-version"] != SPEC_FILE_VERSION:
        raise UnsupportedSpecificationError("Specification version %s is different then the supported one %s" % (spec["spec-version"], SPEC_FILE_VERSION))
    if "bundle" not in spec:
        raise SpecificationError("Missing field `bundle`!")

def parse_artifact_spec(spec):
    """Parse an artifact specification and return the components

    Valid artifact specification:
     * ro.ieat:test:3.4:x86
    """
    match = ARTIFACT_SPECIFICATION_RE.match(spec)
    if match is None:
        raise SpecificationError("Unsupport artifact specification")
    groups = match.groupdict()
    group_id = groups['GROUPID']
    artifact_id = groups['ARTIFACT']
    version = groups['VERSION']
    classifier = groups['CLASSIFIER']
    return group_id, artifact_id, version, classifier


class PackageBuilder(object):
    log = logging.getLogger("PackageBuilder")
    def __init__(self, config = {}):
        self.config = copy.deepcopy(config)
        self.downloader = Downloader()
        self.validate()

    def validate(self):
        validate_spec(self.config)
        if "assembly" not in self.config:
            raise SpecificationError("Missing assembly specification")

    def downloadArtifacts(self):
        assemblySpec = self.config["assembly"]
        download_registry = self.config["me2"]["build"]["download"]
        download_dir = expand_variables("${me2.build.download_dir}", self.config)
        download_dir = os.path.normcase(download_dir)

        if not 'fetch' in assemblySpec:
            self.log.debug('Nothing to download')
            return
        else:
            self.log.debug("Download dir: %s", download_dir)

        if not os.path.exists(download_dir):
            self.log.info("Creating download directory: %s", download_dir)
            os.makedirs(download_dir)
        fetchList = assemblySpec['fetch']
        for entry in fetchList:
            name = entry["name"]
            if name in download_registry: # Already registered, should not happen
                self.log.error("Artifact %s marked already as downloaded!", name)
                continue
            url = expand_variables(entry["url"], self.config)
            destination = os.path.normcase(expand_variables(entry["destination"], self.config))
            self.log.info("Downloading %s -> %s", url, destination)
            self.downloader.fetch(url, destination)
            download_registry[name] = {'file': destination}
            self.log.info("Download finished!")
            if "action" in entry:
                self.log.info("Running post download actions")
                self.do_post_download(name, entry)

    def do_post_download(self, name, entry):
        action = entry["action"]
        operation = action["operation"]
        input_file = self.config["me2"]["build"]["download"][name]['file']
        if operation == "extract":
            extract_dir = os.path.normcase(expand_variables(action['destination'], self.config))
            self.extract(input_file, extract_dir, options = action)
        else:
            self.log.critical("Operation %s is not supported!", operation)


    def extract(self, infile, outdir, options):
        log = self.log.getChild("extract")
        archive_type = options['type']
        if archive_type not in ["tgz", "tbz", "tar.gz", "tar.bz2"]:
            log.critical("Unsupport archive type: %s", archive_type)
            return
        log.info("Extracting file %s into directory %s", infile, outdir)

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        exclude = options["exclude"]
        tar = tarfile.open(infile, "r:*")
        for item in tar:
            if any(map(lambda x: fnmatch.fnmatchcase (item.name, x), exclude)):
                log.info("Ignoring file %s", item.name)
                continue
            try:
                log.debug("Extracting %s", item.name)
                tar.extract(item.name, path = outdir)
            except EnvironmentError, e:
                log.warn("Failed to extract %s: %s", item.name, e)
        tar.close()

    def repack(self, task):
        log = self.log.getChild("repack")
        infile = expand_variables(task['source'], self.config)
        destfile = expand_variables(task['destination'], self.config)
        compresion_type = expand_variables(task['compression-type'], self.config)
        exclude = task['exclude']
        inject = task['inject']

        if compresion_type is None:
            compression_flag = ""
        elif compresion_type not in ["gz", "bz2", ""]:
            raise SpecificationError("Unsupported compression format '%s'" % compresion_type)
        else:
            compression_flag = compresion_type
        if os.path.exists(destfile):
            os.remove(destfile)
        #ToDo: check that the file exists 
        in_tar = tarfile.open(infile, "r:*")
        out_tar = tarfile.open(destfile, "w:%s" % compression_flag, format = tarfile.GNU_FORMAT)
        try:
            # Copy between archives
            for item in in_tar.getmembers():
                if any(map(lambda x: fnmatch.fnmatchcase (item.name, x), exclude)):
                    log.debug("Ignoring file %s", item.name)
                    continue

                if item.isfile():
                    log.debug("Adding regular file %s", item.name)
                    fle = in_tar.extractfile(item)
                    out_tar.addfile(item, fle)
                else:
                    log.debug("Adding special file %s", item.name)
                    out_tar.addfile(item)
            # Inject files
            for entry in inject:
                raw_source, destination = entry
                source = expand_variables(raw_source, self.config)
                destination = expand_variables(destination, self.config)
                if not os.path.exists(source):
                    raise SpecificationError("File %s (%s) does not exist" % (raw_source, source))
                out_tar.add(source, destination)

        finally:
            out_tar.close()
            in_tar.close()


    def runTasks(self):
        log = self.log.getChild("runTasks")
        tasks_spec = self.config["assembly"]['tasks']
        for task in tasks_spec:
            operation = task["operation"]
            if operation == "repack":
                self.repack(task)
            else:
                log.critical("Operation %s is not supported", operation)

    def saveDescriptor(self):
        log = self.log.getChild("saveDescriptor")
        bundle_dir = os.path.normcase(expand_variables("${me2.build.bundle_dir}", self.config))
        desc_file = os.path.join(bundle_dir, "build_configuration.json")
        bundle_desc_file = os.path.join(bundle_dir, SPEC_FILE_NAME)
        log.debug("Saving descriptor to: %s", bundle_desc_file)

        self.log.debug("Saving build time descriptor to %s", desc_file)
        with open(desc_file, "w") as f:
            json.dump(self.config, f, sort_keys = True, indent = 4)
        self.log.debug("Saving configuration to %s", bundle_desc_file)
        with open(bundle_desc_file, "w") as f:
            json.dump(self.getBundleConfig(), f, sort_keys = True, indent = 4)


    def getBundleConfig(self):
        config = {"spec-version": SPEC_FILE_VERSION}
        config["bundle"] = self.config["bundle"]
        config["configuration"] = self.config["configuration"]
        return config


    def createBundle(self):
        log = self.log.getChild("createBundle")
        bundle_name = expand_variables("${me2.bundle_name}", self.config)
        bundle_file = os.path.normcase(expand_variables("${me2.build.bundle}", self.config))
        bundle_dir = os.path.normcase(expand_variables("${me2.build.bundle_dir}", self.config))
        log.info("Destination bundle: %s", bundle_file)
        if os.path.exists(bundle_file):
            log.warn("bundle file exists and it will be removed: %s", bundle_file)
            os.remove(bundle_file)

        with zipfile.ZipFile(bundle_file, 'w', allowZip64 = True, compression = zipfile.ZIP_DEFLATED) as bundle:
            bundle.comment = "mOSAIC Bundle for %s" % bundle_name
            log.debug("Creating bundle with files from: %s", bundle_dir)
            manifest = StringIO.StringIO()
            for dirpath, dirnames, filenames in os.walk(bundle_dir):
                arc_dir = os.path.relpath(os.path.abspath(dirpath), bundle_dir)
                for dir_file in filenames:
                    efective_path = os.path.join(dirpath, dir_file)
                    arc_path = os.path.join(arc_dir, dir_file)
                    if not os.path.exists(efective_path):
                        log.warn("File %s does not exist !", efective_path)
                        continue
                    fsize = os.path.getsize(efective_path)
                    fhash = sha1file(efective_path)
                    manifest.write("%(fname)s\t%(fsize)d\t%(fhash)s\n" % {'fname': arc_path, 'fsize': fsize, 'fhash': fhash})
                    bundle.write(efective_path, arc_path)
            bundle.writestr("./MANIFEST.mf", manifest.getvalue())
            manifest.close()

        return Bundle(bundle_file)

    def build(self):
        self.make_dirs()
        self.log.info("Validateing specification")
        self.validate()
        self.log.info("Downloading Artifacts")
        self.downloadArtifacts()
        self.log.info("Running tasks")
        self.runTasks()
        self.log.info("Saving build time descriptor")
        self.saveDescriptor()
        self.log.info("Creating bundle")
        bundles = self.createBundle()
        return [bundles, ]

    def make_dirs(self):
        bundle_dir = expand_variables("${me2.build.bundle_dir}", self.config)
        bundle_dir = os.path.normcase(bundle_dir)
        if not os.path.exists(bundle_dir):
            os.makedirs(bundle_dir)

class BundleInfo(object):
    specification = None
    group_id = None
    package_id = None
    version = None
    type = None
    classifier = None

class Bundle(object):
    log = logging.getLogger("Bundle")
    info = None
    def __init__(self, *args, **argv):
        log = self.log.getChild("__init__")
        if self.info is not None:
            return
        if 'package_file' in argv: package_file = argv['package_file']
        elif len(args) >= 1: package_file = args[0]
        else: raise AttributeError("Missing package_file attribute")

        if isinstance(package_file, basestring):
            self.package_file_path = package_file
        else:
            self.package_file_path = package_file.name
        log.debug("Opening bundle file %s", os.path.abspath(self.package_file_path))
        self.package_file = zipfile.ZipFile(package_file)
        self.info = self._get_info()
        specialized_class = None
        for klass in Bundle.__subclasses__():
            if klass.type == self.info.type:
                specialized_class = klass
        if specialized_class is None:
            raise UnsupportedBundle("The bundle type %s" % self.info.type)
        self.__class__ = specialized_class

        specialized_class.__init__(self, package_file, *args, **argv)

    def _get_info(self):
        bi = BundleInfo()
        spec = json.load(self.package_file.open(SPEC_FILE_NAME))
        bundle = spec['bundle']
        bi.configuration = spec['configuration']
        bi.identification = ":".join((bundle['group-id'], bundle['package-id'], bundle['version']))
        if 'classifier' in bundle:
            bi.identification += ":%s" % bundle['classifier']
        bi.type = bundle["type"]
        bi.group_id = bundle['group-id']
        bi.package_id = bundle['package-id']
        bi.version = bundle['version']
        bi.classifier = bundle.get("classifier", None)
        bi.bundle_info = bundle
        return bi

    def extract(self, destination):
        raise NotImplementedError()

class ContainerBundle(Bundle):
    type = "container-bundle"
    log = logging.getLogger("ContainerBundle")

    def extract(self, destination):
        self.log.debug("Extracting into: %s", destination)
        self.extract_rootfs(os.path.join(destination, "rootfs"))
        self.extract_meta(destination)
        return self

    def extract_meta(self, destination):
        self.log.debug("Saving metadata to %s", destination)
        configuration_file = os.path.join(destination, "configuration.json")
        bundle_file = os.path.join(destination, "bundle.json")
        with open(configuration_file, "w") as f:
            json.dump(self.info.configuration, f)
        with open(bundle_file, "w") as f:
            json.dump(self.info.bundle_info, f)

    def extract_rootfs(self, destination):
        self.log.debug("Extracting rootfs into: %s", destination)
        os.makedirs(destination)
        tar_object = zip_file_buffer(open(self.package_file_path), "rootfs")
        tar = tarfile.open(fileobj = tar_object, mode = "r|")
        tar.extractall(destination)
        self.log.debug("Finished extracting!")




class Packager(object):
    log = logging.getLogger("Packager")
    def __init__(self, default_config = DEFAULT_CONFIG_FILE):
        if os.path.exists(default_config):
            self.log.info("Loading config from: %s", default_config)
            self.config = json.load(open(default_config))
        else:
            self.log.debug("Starting with empty config")
            self.config = {'me2': {}}


        self.config_file = os.path.join(os.getcwd(), SPEC_FILE_NAME)
        try:
            self.config.update(json.load(open(self.config_file)))
        except ValueError,e:
            self.log.warn("Failed parsing spec file from %s", self.config_file)
            raise BundleSpecError("Failed parsing spec file")
        me2_config = self.config["me2"]
        me2_config['cwd'] = os.getcwd()
        me2_config['bundle_name'] = "${bundle.package-id}-${bundle.version}-${bundle.classifier}"

    def __call__(self, options):
        self.handle(options)

    def setup_parser(self, parser):
        parser.add_argument('--directory', type = str, default = ".", help = "Base directory of bundle")
        subparsers = parser.add_subparsers(help = 'commands')
        validate_parser = subparsers.add_parser('validate', help = 'Validate a package')
        validate_parser.set_defaults(package_command = self.validate)

        build_parser = subparsers.add_parser('build', help = 'Validate a package')
        build_parser.add_argument("--buildDir", type = str, default = "${me2.cwd}/me2-build")
        build_parser.add_argument("--upload", action = 'store_true', default = False)
        build_parser.add_argument("--repository", type = str, default = "http://developers.mosaic-cloud.eu/artifactory/mosaic")
        build_parser.set_defaults(package_command = self.build)

        extract_parser = subparsers.add_parser('extract', help = 'extract a package')
        extract_parser.add_argument("--bundle", type = str, help = "The bundle file that should be extracted")
        extract_parser.set_defaults(package_command = self.extract)

    def validate(self, options):
        raise NotImplementedError()

    def extract(self, options):
        raise NotImplementedError()

    def upload(self, repository, bundles):
        self.log.debug("Starting upload")
        repo = Repository("upload", repository)
        for bundle in bundles:
            repo.register(bundle)


    def build(self, options):
        config = copy.deepcopy(self.config)
        if 'build' in config['me2']:
            build_config = config['me2']['build']
        else:
            build_config = {}
            config['me2']['build'] = build_config

        build_config['build_dir'] = options.buildDir
        build_config['bundle'] = os.path.join("${me2.build.build_dir}", "${me2.bundle_name}.mb")
        build_config['download_dir'] = os.path.join("${me2.build.build_dir}", "download")
        build_config["extract_dir"] = os.path.join("${me2.build.build_dir}", "extract")
        build_config["bundle_dir"] = os.path.join("${me2.build.build_dir}", "bundle")
        build_config["resource_dir"] = os.path.join("${me2.cwd}", "resources")
        if 'download' not in build_config:
            build_config["download"] = {}

        builder = PackageBuilder(config = config)
        bundles = builder.build()
        if options.upload:
            self.upload(options.repository, bundles)

    def handle(self, options):
        options.package_command(options)


