from distutils.core import setup

setup(
    name='readSelector',
    version='0.1.0',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['readselector', 'readselector.test'],
    scripts=['bin/readSelector'],
    url='http://pypi.python.org/pypi/readSelector/',
    license='LICENSE.txt',
    description='readSelector',
    long_description=open('README.txt').read(),
    install_requires=[],
)
