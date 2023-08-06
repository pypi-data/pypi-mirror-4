import os

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = '0.1.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name='scss_tools',
    version=version,
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    description='A bundle of tools for making web development with SCSS in Python much easier',
    long_description=README + '\n\n' + CHANGES,
    keywords='css oocss xcss sass scss less precompiler monitor',
    url='https://bitbucket.org/victorlin/scss_tools',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'PyYaml',
        'pyScss',
        'watchdog'
    ], 
    entry_points="""\
    [console_scripts]
    scss_monitor = scss_tools.monitor:main
    scss_compile = scss_tools.compiler:main
    """
)
