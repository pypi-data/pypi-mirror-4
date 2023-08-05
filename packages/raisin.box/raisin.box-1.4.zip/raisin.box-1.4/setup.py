from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'configobj',
]

entry_points = """
    # -*- Entry points: -*-
    """

classifiers = [
    'Programming Language :: Python',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Operating System :: POSIX :: Linux',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
]

with open("README.txt") as f:
    README = f.read()

with open("CHANGES.txt") as f:
    CHANGES = f.read()

setup(name='raisin.box',
      version='1.4',
      packages=find_packages(),
      description=("A package used in the Raisin web application"),
      long_description=README + '\n' + CHANGES,
      author='Maik Roder',
      author_email='maikroeder@gmail.com',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      keywords='RNA-Seq pipeline ngs transcriptome bioinformatics ETL',
      url='http://big.crg.cat/services/grape',
      license='gpl',
      namespace_packages=['raisin'],
      entry_points=entry_points,
      )
