from distutils.core import setup

setup(
    name='RMASAdapter',
    version='0.1.0',
    author='Jason Marshall',
    author_email='j.j.marshall@kent.ac.uk',
    packages=['rmas_adapter', 
              'rmas_adapter.conf', 
              'rmas_adapter.conf.adapter_template',
              'rmas_adapter.core', ],
    scripts=['rmas_adapter/bin/rmas_adapter_admin.py'],
    url='http://pypi.python.org/pypi/RMASAdapter/',
    license='LICENSE.txt',
    description='A basic framework for building RMAS adapters',
    long_description=open('README.md').read(),
    install_requires=[
        "suds == 0.4",
        "lxml == 3.0",
    ],
)