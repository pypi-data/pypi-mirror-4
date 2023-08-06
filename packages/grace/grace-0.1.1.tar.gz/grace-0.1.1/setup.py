from glob import glob
import os
from setuptools import setup

data_files = [
    ('', ['LICENSE.txt']),
    ('', ['README.txt'])
]

previous = ''
for root, dirs, files in os.walk(os.path.join('grace_package', 'skeleton')):
    for filename in files:
        if previous != root:
            data_files.append((root, glob(root + '/*.*')))
            previous = root

setup(
    name='grace',
    description='A tool to simplify JavaScript development.',
    author='Michael Diener',
    author_email='dm.menthos@gmail.com',
    url='https://github.com/mdiener/grace',
    version='0.1.1',
    license='LICENSE.txt',
    scripts=['bin/grace.py'],
    packages=['grace'],
    install_requires=['libsass'],
    data_files=data_files,
    keywords='toolchain javascript dizmo js buildtool',
    long_description=open('README.txt').read(),
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
