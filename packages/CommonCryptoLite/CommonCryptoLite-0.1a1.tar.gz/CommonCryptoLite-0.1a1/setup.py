from distutils.core import setup, Extension

setup(
	name='CommonCryptoLite',
	version='0.1a1',
	author_email='jwight@schwa.io',
	author='Jonathan Wight',
	description='CommonCrypto',
	url='http://schwa.io/',
	ext_modules = [Extension('CommonCryptoLite', ['CommonCryptoLite.c'])],
	zip_safe = True,
	)
