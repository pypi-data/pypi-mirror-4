# This is your "setup.py" file.
# See the following sites for general guide to Python packaging:
#   * `The Hitchhiker's Guide to Packaging <http://guide.python-distribute.org/>`_
#   * `Python Project Howto <http://infinitemonkeycorps.net/docs/pph/>`_

from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.3.0'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='annopyte',
    version=version,
    description="python based tool for annotation and annotation processing.",
    long_description=README,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    # classifiers=[c.strip() for c in """
    #     Development Status :: 4 - Beta
    #     License :: OSI Approved :: MIT License
    #     Operating System :: OS Independent
    #     Programming Language :: Python :: 2.6
    #     Programming Language :: Python :: 2.7
    #     Programming Language :: Python :: 3
    #     Topic :: Software Development :: Libraries :: Python Modules
    #     """.split('\n') if c.strip()],
    # ],
    keywords='annotations metadata',
    author='Alan Franzoni',
    author_email='username@franzoni.eu',
    url='http://annopyte.franzoni.eu',
    license='APL 2.0',
    packages=find_packages("."),
    package_dir = {'': "."},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
