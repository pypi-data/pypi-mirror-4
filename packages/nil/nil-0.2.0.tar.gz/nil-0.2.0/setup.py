from setuptools import setup, find_packages
import sys, os

version = "0.2.0"

install_requires=[
]

if sys.version_info < (2, 7):
    install_requires.append('argparse')

setup(name='nil',
      version=version,
      description='CMGS cOde ToOls',
      long_description="",
      classifiers=[], # Get strings from http://bit.ly/tYt3j
      keywords='',
      author="Kelvin Peng",
      author_email="ilskdw@gmail.com",
      url="http://hg.cmgs.me/",
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples*', 'tests*']),
      include_package_data=True,
      install_requires=install_requires,
      zip_safe=False,
      entry_points="""
      [console_scripts]
      nil-clean = nil.clean:main
      """,
      tests_require=['nose'],
      test_suite='nose.collector',
)
