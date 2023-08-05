from distutils.core import setup

setup(
    name='MPInfo',
    version='0.2.0',
    author='Robert Day',
    author_email='rkd@rkd.me.uk',
    packages=['mpinfo'],
    scripts=['bin/postcode_json.py'],
    url='http://pypi.python.org/pypi/MPInfo/',
    license='LICENSE.txt',
    description='Utilities to retrieve details about an United Kingdom MP from http://parliament.uk.',
    long_description=open('README.txt').read(),
    install_requires=['beautifulsoup4'],
)
