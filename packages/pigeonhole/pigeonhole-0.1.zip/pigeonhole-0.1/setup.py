from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
]

entry_points = """
      [console_scripts]
      pigeonhole = pigeonhole:main
      """

classifiers = [
    'Programming Language :: Python',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
]

with open("README.txt") as f:
    README = f.read()

with open("CHANGES.txt") as f:
    CHANGES = f.read()

setup(name='pigeonhole',
      version='0.1',
      packages=find_packages(),
      description=("Dashboard development tool"),
      long_description=README + '\n' + CHANGES,
      author='Maik Roeder',
      author_email='roeder@berg.net',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      keywords='',
      url='https://github.com/maikroeder/pigeonhole.git',
      license='gpl',
      entry_points=entry_points,
      )
