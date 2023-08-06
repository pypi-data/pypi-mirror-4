from distutils.core import setup

setup(
	name = "pyta",
	version = '0.1.1',
	author = 'valtron',
	author_email = 'valtron2000+pyta@gmail.com',
	py_modules = ['pyta'],
	url = 'https://github.com/valtron/pyta',
	license = 'BSD',
	description = "Inner Method Dispatch for Python",
	long_description = open('README.rst').read(),
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
	]
)
