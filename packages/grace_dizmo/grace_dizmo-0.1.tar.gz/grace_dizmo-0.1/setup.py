from glob import glob
import os
from setuptools import setup

data_files = [
    ('', ['LICENSE.txt'])
]

previous = ''
for root, dirs, files in os.walk('skeleton'):
    for filename in files:
        if previous != root:
            data_files.append((root, glob(root + '/*.*')))
            previous = root

setup(
    name='grace_dizmo',
    description='A plugin for grace',
    author='Michael Diener',
    author_email='dm.menthos@gmail.com',
    url='https://github.com/mdiener/grace-dizmo',
    version='0.1',
    license='LGPL3',
    py_modules=['grace_dizmo'],
    install_requires=['grace'],
    data_files=data_files,
    keywords='toolchain javascript dizmo js buildtool',
    classifiers=[
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Intended Audience :: Developers',
        'Environment :: Console'
    ]
)
