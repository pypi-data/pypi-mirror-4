from setuptools import setup, find_packages
version = '2.8.6'

required_packages = ['psutil >= 0.3.0', 'MYSQL-python']
setup(name='gurumate',
      description="A library of platform-independent tools that ease gathering information about the system.",
      long_description="A library of platform-independent tools that ease gathering information about the system. \
      It powers the SimTry practice environment and enables the patented gurumate technology to provide accurate hints. \
      The Gurumate SDK is platform agnostic and it currently supports Linux and Windows operating systems;  \
      it is also extensible and grows to support whatever the new labs need.",
      version=version,
      url='http://confluence.cloud9ers.com/display/TGILA/Gurumate+SDK',
      author="Cloud Niners Ltd.",
      author_email="support@cloud9ers.com",
      packages=find_packages(exclude=['tests', 'tests.*']),
      package_data={'gurumate':['linux2/*.py', 'win32/*.py']},
      zip_safe=False,
      install_requires=required_packages,
      license="LGPLv3",
      classifiers=['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                     'Operating System :: Microsoft :: Windows :: Windows 7',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: Software Development :: Libraries :: Application Frameworks'],

      )
