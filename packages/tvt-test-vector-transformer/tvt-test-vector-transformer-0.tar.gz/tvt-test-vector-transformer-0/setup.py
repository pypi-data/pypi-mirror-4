
from glob import glob
from distutils.core import setup
from setuptools import find_packages

URL = 'https://github.com/gitfoxi/' \
      'tvt-test-vector-transformer'

setup(
    name='tvt-test-vector-transformer',
    version=0,
    description='Translate digital test vectors for automated test '
                'equipment for semiconductors',
    author='Michael Fox',
    author_email='415fox@gmail.com',
    url=URL,
    download_url=URL + '/tarball/master',
    use_2to3=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: "
        "Electronic Design Automation (EDA)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(),
    scripts=glob("Scripts/*.py"),
)
