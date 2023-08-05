import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), fname)).read()

setup(
    name = 'zyzz',
    version = '1.0.0',
    description = u'Python util modules',
    long_description = read('README.rst'),
    author = 'Dmitry Bashkatov',
    author_email = 'dbashkatov@gmail.com',
    url = 'http://github.com/nailgun/zyzz/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console', 'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
    ],
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    include_package_data = True,
    install_requires = [],
)
