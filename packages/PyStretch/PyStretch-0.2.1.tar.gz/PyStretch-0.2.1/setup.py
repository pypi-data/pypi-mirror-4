from distutils.core import setup

setup(
    name='PyStretch',
    version='0.2.1',
    author='Jay Laura',
    author_email='jlaura@asu.edu',
    packages=['pystretch', 'pystretch.core', 'pystretch.filter',
              'pystretch.linear', 'pystretch.masks','pystretch.nonlinear',
              'pystretch.plot', 'pystretch.tests', 'pystretch.custom'],
    scripts=['bin/pystretcher.py', 'bin/pystretch_test.py'],
    url='http://pypi.python.org/pypi/PyStretch/',
    license='LICENSE.txt',
    description='Python image analysis and manipulation',
    long_description=open('README.txt').read(),
    requires=['numpy', 'scipy', 'matplotlib'],
)
