from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.2.2'

install_requires = [
    "pyparsing <2"
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='boolparser',
    version=version,
    description="Boolean Parser",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='Boolean, Parsing',
    author='Christopher Lee',
    author_email='lee@foldmountain.com',
    url='http://github.com/eelsirhc/boolparser',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['boolparser_test=boolparser:test_parser',
            ]
    }
)
