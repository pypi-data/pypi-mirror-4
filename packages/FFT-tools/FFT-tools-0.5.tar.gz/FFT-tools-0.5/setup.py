"Wrap NumpPy's FFT routines to reduce clutter."

from distutils.core import setup
import os.path

from FFT_tools import __version__


package_name='FFT-tools'
_this_dir = os.path.dirname(__file__)

setup(name=package_name,
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url='http://blog.tremily.us/posts/{}/'.format(package_name),
      download_url='http://git.tremily.us/?p={}.git;a=snapshot;h={};sf=tgz'.format(package_name, __version__),
      license='GNU General Public License (GPL)',
      platforms=['all'],
      description=__doc__,
      long_description=open(os.path.join(_this_dir, 'README'), 'r').read(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      py_modules=['FFT_tools'],
      )
