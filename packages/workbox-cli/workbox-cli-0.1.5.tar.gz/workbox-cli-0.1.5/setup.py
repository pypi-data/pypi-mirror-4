from distutils.core import setup
from setuptools import find_packages

install_requires = ['requests', 'configobj>4.7.1']

setup(
    name='workbox-cli',
    version='0.1.5',
    author='Sam Tardif',
    author_email='sam.tardif@gmail.com',
    packages=find_packages(),
    url='http://bitbucket.org/samtardif/workbox-cli',
    license='MIT',
    description='A command line interface for Confluence ToolBox',
    long_description=file('README.txt').read(),
    entry_points = {'console_scripts': ['workbox = workboxcli:main']},
    install_requires = install_requires,
    zip_safe=False,
)
