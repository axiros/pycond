"""
How to upload
python setup.py clean sdist bdist_wheel
twine upload dist/*
"""


# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md')) as fd:
    md = fd.read()

for f in (HERE + '/.README.tmpl.md',):
    with open(f) as fd:
        version = fd.read().split('version:', 1)[1].split('\n', 1)[0]
        version = version.strip()


setup(
    name='pycond',
    version=version,
    description='Lightweight Condition Parsing and Building of Evaluation Expressions',
    long_description=md,
    long_description_content_type='text/markdown',
    # for async rx we assume rx is installed:
    install_requires=[],
    tests_require=['pytest2md>=20190430'],
    include_package_data=True,
    url='https://github.com/axiros/pycond',
    author='gk',
    author_email='gk@axiros.com',
    license='BSD',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Editors :: Text Processing',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        # most will work, tests are done for 3 only though, using py3 excl. constructs:
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords=[
        'conditions',
        'expression',
        'async',
        'serialization',
        'rxpy',
        'reactivex',
    ],
    py_modules=['pycond'],
    entry_points={},
    zip_safe=False,
)
