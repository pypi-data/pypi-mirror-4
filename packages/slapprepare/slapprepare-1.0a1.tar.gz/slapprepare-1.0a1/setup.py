from setuptools import setup, find_packages
import glob
import os

version = '1.0a1'
name = 'slapprepare'


setup(name=name,
      version=version,
      description="SlapOS Setup kit for dedicated SuSE machines.",
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='slapos Setup Kit',
      license='GPLv3',
      url='http://www.slapos.org',
      author='VIFIB',
      packages=['slapprepare'],
      include_package_data=True,
      install_requires=['slapos.libnetworkcache',],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'slapprepare = slapprepare:slapprepare',
              'slapupdate = slapprepare.slapupdate:main',
          ]
      },
)
