from distutils.core import setup 

setup(name              = 'py-gridvid',
      version           = '0.0.3',
      description       = open('../VERSION').read(),
      author            = '',
      author_email      = 'info@cpusage.com',
      maintainer        = 'GridVid',
      maintainer_email  = 'info@gridvid.me',
      url               = 'https://gridvid.me',
      py_modules        = [
          'gridvid'
          ],
      package_dir       = {'' : 'lib'},
      license           = 'GPLv3'
      )
