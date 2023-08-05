from distutils.core import setup

setup(
    name='SmartZ',
    version='0.1.2',
    author='Andy MacKinlay',
    author_email='admackin@gmail.com',
    packages=['smartz'],
    package_dir={'': 'lib'},
    url='http://bitbucket.org/andymackinlay/smartz',
    license='BSD',
    description='Handle gzipped files semi-transparently.',
    long_description=open('README.txt').read(),
)
