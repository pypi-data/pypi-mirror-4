from distutils.core import setup

setup(
    name='Digify',
    version='0.2dev',
    author='Andy MacKinlay',
    author_email='admackin@gmail.com',
    url='https://github.com/admackin/digify',
    packages=['digify',],
    package_dir={'': 'src'},
    license='BSD',
    description='Convert written out numbers to integers',
    long_description=open('README.txt').read(),
)
