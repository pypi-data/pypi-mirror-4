import os
from setuptools import setup, find_packages

def read(fname):
    if os.path.exists(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
      name = "me2-packager",
      version = "0.0.3",
      author = "Marian Neagul",
      author_email = "marian@ieat.ro",
      description = "me2-pack is the packaging component of me2",
      license = "APL",
      keywords = "packaging mOSAIC",
      url = "http://developers.mosaic-cloud.eu",
      namespace_packages = ["me2"],
      package_dir = {'':'src'},
      packages = find_packages("src", exclude = ["*tests*", ]),
      long_description = read('README.rst'),
      classifiers = [
                     "Intended Audience :: System Administrators",
                     "Development Status :: 3 - Alpha",
                     "Topic :: System :: Archiving :: Packaging",
                     "License :: OSI Approved :: Apache Software License",
                     ],
      entry_points = {
                      'console_scripts': [ 'me2pack = me2.packaging.app:main', ]
                      },
      setup_requires=["setuptools_webdav"],
      dependency_links = [
        "http://developers.mosaic-cloud.eu/artifactory/pypi/"
        ],
      install_requires = ["lockfile>=0.9.0", "Python_WebDAV_Library>=0.3.0"]
)
