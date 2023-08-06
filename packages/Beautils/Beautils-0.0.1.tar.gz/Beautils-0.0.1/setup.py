from distutils.core import setup

setup(
    name='Beautils',
    version='0.0.1',
    author_email='kotecha.ravi@gmail.com',
    packages=['beautils'],
    licence='LICENCE.txt',
    description='a module to make Beau stop bitching about time in Python',
    long_description=open('README.md').read(),
    use_2to3=True
)
