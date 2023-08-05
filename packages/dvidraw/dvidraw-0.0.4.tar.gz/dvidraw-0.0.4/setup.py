from distutils.core import setup

setup(name = 'dvidraw',
      packages = ['dvidraw'],
      version = '0.0.4',
      requires = ['dvipy'],
      provides = ['dvidraw'],
      author = 'Dave Mallows',
      author_email = 'dave.mallows@gmail.com',
      url = 'http://dpwm.bitbucket.org/dvidraw',
      description = 'Drawing package with LaTeX-rendered text',
      keywords = 'drawing dvi tex latex',
      license = 'GPLv2')


