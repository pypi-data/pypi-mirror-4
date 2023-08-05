from setuptools import setup
import os
import sys
from libthirty import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

extra = {}
requirements = ['docutils', 'requests', 'docar>=0.9'],
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
    zip_safe=False,  # Don't create egg files, Django cannot find templates
                     # in egg files.
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
        'Topic :: Internet :: WWW/HTTP',
    ],
    **extra
)
