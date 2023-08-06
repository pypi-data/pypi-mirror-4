from distutils.core import setup, Extension

setup(
	name='CommonCryptoLite',
	version='0.1a2',
	author_email='jwight@mac.com',
	author='Jonathan Wight',
	description='CommonCrypto',
	url='http://toxicsoftware.com/',
	zip_safe = False,
	ext_modules = [
		Extension('CommonCryptoLite/CommonCryptoLite', ['CommonCryptoLite/CommonCryptoLite.c'])
		],
	)
