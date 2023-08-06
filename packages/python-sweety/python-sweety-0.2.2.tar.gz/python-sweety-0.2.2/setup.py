from distutils.core import setup

setup(
		name = 'python-sweety',
		version = '0.2.2',
		description = 'Python common utility classes',
		author = 'Chris Chou',
		author_email = 'm2chrischou@gmail.com',
		url = 'https://bitbucket.org/mongmong/python-sweety',
		classifiers = [
			'Programming Language :: Python',
			'Development Status :: 2 - Pre-Alpha',
			'Topic :: Software Development :: Libraries :: Python Modules',
			],
		package_dir = {'': 'src'},
		packages = ['sweety'],
)

