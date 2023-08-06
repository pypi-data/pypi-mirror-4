from distutils.core import setup

setup(
    name='HorizonJPL',
    version='0.1.0',
    author='Matthew Mihok',
    author_email='matthew.mihok@niewma.com',
    packages=['horizon', 'horizon.test'],
    scripts=['standalone.py'],
    url='http://pypi.python.org/pypi/HorizonJPL/',
    license='LICENSE.txt',
    description='Access to NASA\'s JPL HORIZON Ephemeris System',
    long_description=open('README.md').read(),
    install_requires=[
        'pytest-timeout >= 0.3'
    ]
)
