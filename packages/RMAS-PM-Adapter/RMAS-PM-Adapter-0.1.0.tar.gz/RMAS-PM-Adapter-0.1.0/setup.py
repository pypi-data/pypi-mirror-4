from distutils.core import setup

setup(
    name='RMAS-PM-Adapter',
    version='0.1.0',
    author='Jason Marshall',
    author_email='j.j.marshall@kent.ac.uk',
    packages=['rmas_pm_adapter', 
              'rmas_pm_adapter.handlers', 
              'rmas_pm_adapter.dev'
              ],
    url='http://pypi.python.org/pypi/RMAS-OE-Adapter/',
    license='LICENSE.txt',
    description='A basic framework for building RMAS adapters',
    long_description=open('README.md').read(),
    install_requires=[
        "requests == 0.14.1",
        "RMASAdapter == 0.1.4 ",
    ],
)