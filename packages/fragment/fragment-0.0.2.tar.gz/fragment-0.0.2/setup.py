# from distutils.core import setup
from setuptools import setup

setup(
	name='fragment',
	url='https://github.com/zweifisch/fragment',
	version='0.0.2',
	description='just another static site generator',
	author='Feng Zhou',
	author_email='zf.pascal@gmail.com',
	packages=['fragment'],
	package_data={'fragment': ['*.html', 'style.css']},
	install_requires=['markdown2', 'docopt', 'pystache'],
	entry_points={
		'console_scripts': ['fragment=fragment:main'],
	},
)
