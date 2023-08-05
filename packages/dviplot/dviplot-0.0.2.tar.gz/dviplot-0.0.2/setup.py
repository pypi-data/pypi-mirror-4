from distutils.core import setup

setup(name = 'dviplot',
      version = '0.0.2',
      packages = ['dviplot'],
      provides = ['dviplot'],
      requires = ['dvidraw'],
      author = 'Dave Mallows',
      author_email = 'dave.mallows@gmail.com',
      url = 'http://dpwm.bitbucket.org/dviplot',
      description = 'Plotting using DVIdraw',
      keywords = 'chart graph plotting plot dvi tex latex',
      license = 'GPLv2')
