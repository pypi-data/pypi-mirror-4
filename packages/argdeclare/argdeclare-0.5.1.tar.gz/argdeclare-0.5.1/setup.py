from setuptools import setup, find_packages

version = '0.5.1'

setup(name="argdeclare",
      version=version,
      description="Implementation of the interface provided by the cmdln module but using argparse.",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Parnell Springmeyer",
      author_email="ixmatus@gmail.com",
      url="http://bitbucket.org/ixmatus/argdeclare",
      license="PSF",
      zip_safe=False,
      packages=find_packages(),
      requires=['argcomplete'],
      include_package_data=True
      )
