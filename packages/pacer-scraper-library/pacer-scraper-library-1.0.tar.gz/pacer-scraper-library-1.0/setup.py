from distutils.core import setup
setup(name='pacer-scraper-library',
	  version='1.0',
	  author='C Zhang',
	  author_email='admin@uchicagolawandecon.org',
	  maintainer='CSI-LE',
	  url='http://www.uchicagolawandecon.org/research/tools/',
	  description='A library of functions to batch download files from PACER.',
	  long_description='Simple tools to facilitate searching, downloading and \
	  parsing documents from the PACER (Public Access to Court Electronic \
	  Records) database. (An existing PACER account is required).',
	  classifiers=['Development Status :: 4 - Beta', 
				  'Intended Audience :: Legal Industry', 
				  'Intended Audience :: Science/Research', 
				  'License :: OSI Approved :: Python Software Foundation License', 
				  'Natural Language :: English',
				  'Programming Language :: Python :: 2.6',
				  'Topic :: Utilities'],
	  license = 'Python Software Foundation License',
	  py_modules=['pacer_scraper_library'],
	  requires = ['bs4', 'lxml', 'mechanize'],
	  )