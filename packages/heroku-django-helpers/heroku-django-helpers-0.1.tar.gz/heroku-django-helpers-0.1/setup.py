from distutils.core import setup

setup(
	name='heroku-django-helpers',
	version='0.1',
	author='Jack Shedd, Mess',
	author_email='jshedd@thisismess.com',
	packages=['heroku_django_helpers',],
	license='BSD',
	url='http://github.com/thisismess/heroku-django-helpers',
	long_description=open('README.txt').read(),
	install_requires=["Django >= 1.4"]
)