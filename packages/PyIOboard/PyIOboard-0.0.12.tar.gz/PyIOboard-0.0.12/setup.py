from distutils.core import setup

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_PATCH = 12
versionstr = '%s.%s.%s' % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)


setup(
    name='PyIOboard',
    version=versionstr,
    author='Zeb Palmer',
    author_email='zeb@zebpalmer.com',
    packages=['pyioboard'],
    url='http://www.zebpalmer.com',
    license='GPLv3',
    requires=['bottle','paste'],
    description='Webservice to control a Numato lab USB Relay card',
#    long_description=open('README.rst').read(),
    classifiers=[
              'Development Status :: 3 - Alpha',
              'Environment :: Console',
              'Environment :: Plugins',
              'Intended Audience :: Developers',
              'Intended Audience :: System Administrators',
              'Intended Audience :: Telecommunications Industry',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              'Natural Language :: English',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2',
              'Programming Language :: Python :: 2.6',
              'Programming Language :: Python :: 2.7',
              'Topic :: Software Development :: Libraries :: Python Modules',
              'Topic :: Utilities'
              ],
)
