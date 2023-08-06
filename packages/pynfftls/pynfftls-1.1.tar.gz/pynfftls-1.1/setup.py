from distutils.core import setup, Extension

m = Extension('pynfftls',
              libraries = ['m','c','nfft3','fftw3'],
              depends  = ['io.h', 'ls.h','nfft.h', 'utils.h'],
              sources = ['pynfftls.c','nfft.c','ls.c','utils.c'],
              extra_compile_args = ['-finline-functions','-fstrict-aliasing','-malign-double','-std=c99']
              )
#             extra_link_args = ['libdevel.a'],
#              )
#              extra_link_args = ['libdevel.a'] 
#              )
#               extra_compile_args = ['-finline-functions','-I /usr/local/include/','-std=c99'],
#              extra_link_args = ['libdevel.a']) # ,'-Wl,-z,norelro'
#              swig_opts=['-modern', '-I../include'])],
              

setup(name = 'pynfftls',
      version = '1.1',
      description = "Fast Lomb-Scargle periodogram using Non-equispaced Fast Fourier Transform (NFFT)  by B. Leroy",
      author = 'B. Leroy - Python interface by R. Samadi',
      author_email = 'reza.samadi@obspm.fr',
      url =  'http://lesia.obspm.fr/',
      long_description = open('README.txt').read(),
      ext_modules =  [m]
      )
