from setuptools import setup

setup(name = 'mvpoly',
      version = '0.91.3',
      description = 'A library for multivariate polynomials',
      url = 'http://soliton.vm.bytemark.co.uk/pub/jjg/en/code/mvpoly.html',
      author = 'J.J. Green',
      author_email = 'j.j.green@gmx.co.uk',
      license = 'LGPLv3',
      packages = ['mvpoly', 'mvpoly.util'],
      keywords = ['polynomial', 'multivariate', 'numeric'],
      zip_safe = True,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Mathematics'
        ]
      )
