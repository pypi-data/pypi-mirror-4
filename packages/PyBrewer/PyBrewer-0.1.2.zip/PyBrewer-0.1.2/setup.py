from distutils.core import setup

setup(
    name='PyBrewer',
    version='0.1.2',
    author='Anna Novikova',
    author_email='anovikova2718@gmail.com',
    packages=['pybrewer', 'pybrewer.test'],
    url='http://pypi.python.org/pypi/PyBrewer/',
    license='LICENSE.txt',
    description='A Python wrapper for ColorBrewer2.org',
    long_description=open('README.md').read(),
    install_requires=['collections'],
)