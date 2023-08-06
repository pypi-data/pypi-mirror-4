from distutils.core import setup

setup(
    name='Valid EDTF',
    version='0.1.0',
    author='Joseph Liechty',
    author_email='joey.liechty@unt.edu',
    packages=['edtf', 'edtf.test'],
    url='http://pypi.python.org/pypi/valid_edtf/',
    license='LICENSE.txt',
    description='EDTF validation levels 1-3',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyparsing",
        "argparse",
        "datetime"
    ],
)