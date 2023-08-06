from setuptools import setup

setup(
	name='jsonvcs',
	py_modules=['jsonvcs'],
	version='0.0.1',
	author='Sean Lang',
	author_email='slang800@gmail.com',
	url='https://github.com/slang800/jsonvcs',
	license='LICENSE',
	description='version control for structured documents',
	install_requires=[
		"jsonpatch >= 0.11",
	],
)
