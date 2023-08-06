from distutils.core import setup

setup(
	name = 'Python-BrowserStack',
	version = '1.0',
	author = 'Siddharth Saha',
	author_email = 'sidchilling@gmail.com',
	packages = ['browserstack'],
	license = 'MIT',
	long_description = open('README.md').read(),
	install_requires = [
	    "requests"
	    ]
    )
