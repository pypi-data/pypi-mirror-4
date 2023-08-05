from distutils.core import setup

setup(name='dvipy',
      version='0.0.2',
      description='Python library for processing TeX\'s Device Independent output',
      keywords='DVI TeX',
      provides=['dvipy'],
      author='Dave Mallows',
      author_email='dave.mallows@gmail.com',
      license='GPLv2',
      url='http://dpwm.bitbucket.org/dvipy',
      package_data={'dvipy':['templates/*.tex']},
      packages=['dvipy']
     )
