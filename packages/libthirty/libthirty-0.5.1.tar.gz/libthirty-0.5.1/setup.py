from setuptools import setup
import os
import sys
from libthirty import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

extra = {}
requirements = ['docutils', 'requests', 'docar>=0.9.1'],
tests_require = ['nose', 'Mock', 'coverage']

# In case we use python3
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name="libthirty",
    version=__version__,
    packages=['libthirty'],
    package_data={
        'libthirty': ["ssl/StartSSL_CA.pem"],
    },
    include_package_data=True,
    install_requires=requirements,

    tests_require=tests_require,
    setup_requires='nose',
    test_suite="nose.collector",
    extras_require={'test': tests_require},

    author="Christo Buschek",
    author_email="crito@30loops.net",
    url="https://github.com/30loops/libthirty",
    description="libthirty provides a python api to access the 30loops\
platform.",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    **extra
)
