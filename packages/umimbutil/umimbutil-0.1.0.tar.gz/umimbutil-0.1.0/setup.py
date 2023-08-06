from distutils.core import setup

setup(
    name='umimbutil',
    version='0.1.0',
    author='Tom MacWright',
    author_email='tom@macwright.org',
    packages=['mbutil'],
    scripts=['mb-util'],
    url='https://github.com/urbanmapping/mbutil',
    license='LICENSE.md',
    description='An importer and exporter for MBTiles',
    long_description=open('README.md').read(),
)
