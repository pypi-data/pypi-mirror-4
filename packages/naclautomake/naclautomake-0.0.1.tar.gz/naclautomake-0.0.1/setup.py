from setuptools import setup
import naclautomake

setup(name = 'naclautomake',
      version = naclautomake.__version__,
      description = 'Automake of Native Client from Google',
      license = 'Creative Commons Attribution 3.0 Unported License',
      author = 'Alex Chi',
      author_email = 'alex@alexchi.me',
      url = 'http://alexchi.me/',
      packages = ['naclautomake'],
      keywords = '',
      classifiers = [
                     "Programming Language :: Python",
                     "Programming Language :: Python :: 2.7",
                     "Development Status :: 1 - Planning",
                     "License :: OSI Approved",
                     "Operating System :: OS Independent",
                     "Topic :: Software Development",
                     "Topic :: Utilities",
                    ],
      long_description = 'Automake of Native Client from Google')