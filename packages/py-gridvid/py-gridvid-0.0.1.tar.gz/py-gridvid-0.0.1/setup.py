from distutils.core import setup 

setup(name              = 'py-gridvid',
      version           = '0.0.1',
      description       = open('../VERSION').read(),
      author            = 'Christopher J. Hanks',
      author_email      = 'cjhanks@cpusage.com',
      maintainer        = 'GridVid',
      maintainer_email  = 'info@gridvid.me',
      url               = 'https://gridvid.me',
      py_modules        = [
          'gridvid'
          ],
      #packages          = ['gridvid'],
      package_dir       = {'' : 'lib'},
      license           = 'GPLv3'
      )
