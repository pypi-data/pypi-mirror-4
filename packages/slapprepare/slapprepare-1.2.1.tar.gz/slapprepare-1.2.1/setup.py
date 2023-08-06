from setuptools import setup

version = '1.2.1'
name = 'slapprepare'
long_description = open("README.txt").read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

setup(name=name,
      version=version,
      description="SlapOS Setup kit for dedicated SuSE machines.",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='slapos Setup Kit',
      license='GPLv3',
      url='http://www.slapos.org',
      author='VIFIB',
      packages=['slapprepare'],
      include_package_data=True,
      install_requires=[
          'slapos.libnetworkcache',
          'iniparse',
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'slapprepare = slapprepare.autoupdate:main',
              'slapprepare-raw = slapprepare.slapprepare:main',
              'slapupdate = slapprepare.slapupdate:main',
          ]
      },
)
