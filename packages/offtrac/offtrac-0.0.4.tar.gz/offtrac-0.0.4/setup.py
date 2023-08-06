from distutils.core import setup
import glob

setup(name='offtrac',
      version='0.0.4',
      description='Trac xmlrpc library',
      author='Jesse Keating',
      author_email='jkeating@redhat.com',
      url='http://fedorahosted.org/offtrac',
      license='GPLv2+',
      package_dir = {'': 'src'},
      packages = ['offtrac'],
      )
