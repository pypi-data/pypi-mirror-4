import os
from setuptools import setup, find_packages

def read(fname):
    if os.path.exists(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
      name = "me2-supervisor",
      version = "0.0.3",
      author = "Marian Neagul",
      author_email = "marian@ieat.ro",
      description = "me2 is a mOSAIC Cloud Project component responsible for the deployment and supervision of application",
      license = "APL",
      keywords = "deployment mosaic",
      url = "http://developers.mosaic-cloud.eu",
      namespace_packages = ["me2"],
      package_dir = {'':'src'},
      packages = find_packages("src", exclude = ["*tests*", ]),
      long_description = read('README.rst'),
      include_package_data = True,
      package_data = {
                      'me2.server.lxc': ["data/*.mak", "data/templates/*.mak"],
                      'me2.server.web': ["templates/static/*/*", "templates/*.html"],
                      'me2.server': ["data/*.mak"]
                      },
      classifiers = [
                     "Intended Audience :: Developers",
                     "Development Status :: 3 - Alpha",
                     "Topic :: System :: Installation/Setup",
                     "License :: OSI Approved :: Apache Software License",
                     ],
      entry_points = {
                      'console_scripts': [
                                          'mded = me2.server.apps.mded:main',
                                          ]
                      },
      dependency_links = [
        "http://developers.mosaic-cloud.eu/artifactory/pypi/"
        ],
      install_requires = ["mjsrpc2==0.0.6", "lockfile>=0.9.0", "python-daemon>=1.6", "pyyaml>=3.0", "mako>=0.6.0", "me2-packager"]
)
