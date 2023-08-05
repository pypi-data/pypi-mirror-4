import os
from setuptools import find_packages, setup

import hglock

HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README')).read()
VERSION = hglock.__version__


setup(name='hglock',
    version=VERSION,
    description='This extension impliments a centralized file-based locking scheme for Mercurial.',
    long_description=README,
    classifiers=['Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control'
    ],
    keywords='mercurial locking',
    author='aragost Trifork',
    author_email='mg@aragost.com',
    maintainer='Lantiq',
    maintainer_email='MUC-LQ-ADM-HG-U@lantiq.com',
    url='https://bitbucket.org/lantiq/hglock',
    license='GNU GPLv2+',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
