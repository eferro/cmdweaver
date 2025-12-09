from setuptools import setup, find_packages

long_description = open('README.md').read()

setup(
    name='cmdweaver',
    version='0.9.3',
    author='Eduardo Ferro Aldama',
    author_email='eduardo.ferro.aldama@gmail.com',
    description='Extensible command line processor for "ad hoc" shells creation',
    long_description=long_description,
    license='MIT',
    platforms='Linux',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
)
