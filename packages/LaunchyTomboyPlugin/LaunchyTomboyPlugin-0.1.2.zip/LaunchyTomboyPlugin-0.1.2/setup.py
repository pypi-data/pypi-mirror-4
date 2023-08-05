import sys, os
from setuptools import setup, find_packages

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

setup(
    name = "LaunchyTomboyPlugin",
    version = '0.1.2',
    description = "A plugin for Launchy to put Tomboy note titles in the catalog",
    long_description= '\n\n'.join((README, CHANGELOG)),
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://bitbucket.org/rsyring/launchytomboyplugin',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
      ],
    license='BSD',
    packages=['launchytomboyplugin'],
    include_package_data = True,
    zip_safe=False,
)
