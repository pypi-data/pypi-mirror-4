from distutils.core import setup, Extension


m = Extension('pymt64',
               libraries = ['m'],
              depends  = ['mt64mp.h'],
               sources   = ['pymt64.c','mt19937-64mp.c'] )

setup(name = 'PyMT64',
      version = '1.0',
      description = 'Python version of the Mersenne Twister 64-bit pseudorandom number generator',
      author = 'R. Samadi',
      author_email = 'reza.samadi@obspm.fr',
      url =  'http://lesia.obspm.fr/',
      long_description = open('README.txt').read(),
      ext_modules =  [m]
      )
