from distutils.core import setup
from setuptools import find_packages
import os
import sys
from subprocess import Popen,PIPE

README = open('README.rst').read()

def all_files(path,num_root_dir_to_skip=1):
    all= map(lambda x: x.strip(),Popen(['find',path],stdout=PIPE).stdout.readlines())
    return map(lambda x: '/'.join(x.split('/')[num_root_dir_to_skip:]), filter(os.path.isfile,all))

setup(name='StarClusterExtensions',
    version='0.0.1',
    description = "StarCluster Extensions",
    author='Erik Gafni',
    license='Non-commercial',
    long_description=README,
    packages=find_packages(),
    scripts=['bin/sce'],
    package_data={'sce':all_files('sce/sge_plus/data')+all_files('sce/erik/data')},
    install_requires=[
        'starcluster'
    ]
)