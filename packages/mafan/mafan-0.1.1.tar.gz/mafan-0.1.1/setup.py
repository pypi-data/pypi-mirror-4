from distutils.core import setup

setup(
    name='mafan',
    version='0.1.1',
    author='Herman Schaaf',
    author_email='herman@ironzebra.com',
    packages=['mafan'],
    scripts=['bin/convert.py'],
    url='https://github.com/hermanschaaf/mafan',
    license='LICENSE.txt',
    description='A toolbox for working with the Chinese language in Python',
    long_description=open('README.md').read(),
    install_requires=[
        "argparse == 1.2.1",
        "chardet == 2.1.1",
        "wsgiref == 0.1.2",
    ],
)