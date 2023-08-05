from distutils.core import setup

setup(name='Crawl',
	  version='0.1',
	  url='https://github.com/OiNutter/crawl',
	  download_url='https://nodeload.github.com/OiNutter/crawl/legacy.tar.gz/master',
	  description='Python tool for finding files in a set of paths. Based on the Hike ruby gem',
	  author='Will McKenzie',
	  author_email='will@oinutter.co.uk',
	  packages=['crawl'],
	  package_dir={'crawl': 'crawl'}
	  )