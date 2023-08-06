from distutils.core import setup, Extension

setup(
	name='CommonCryptoLite',
	version='0.1a6',
	author_email='jwight@mac.com',
	author='Jonathan Wight',
	description='CommonCrypto',
	url='https://github.com/schwa/Python-CommonCryptoLite',

	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: MacOS X',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: MacOS :: MacOS X',
		'Topic :: Security :: Cryptography',
		],
	license = 'BSD License',

	platforms = 'Mac OS X',

	ext_modules = [
		Extension('CommonCryptoLite', ['CommonCryptoLite.c'])
		],
	)
