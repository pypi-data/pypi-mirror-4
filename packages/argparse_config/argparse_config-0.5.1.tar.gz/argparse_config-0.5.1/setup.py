from setuptools import setup, find_packages
from argparse_config import __version__

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='argparse_config',
    version=__version__,
    description="Default values for argparse commandline args read from a config file.",
    long_description=readme(),
    url='http://bitbucket.org/tikitu/argparse_config',
    author='Tikitu de Jager',
    author_email='tikitu@logophile.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    keywords='',
    packages=find_packages('.'),
    package_dir = dict((
      ('', '.'),
    )),
    entry_points=dict(
        console_scripts=[],
    ),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    tests_require=['nose'],
)
