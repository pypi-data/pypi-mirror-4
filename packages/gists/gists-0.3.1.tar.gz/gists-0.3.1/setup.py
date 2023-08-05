import os
from setuptools import setup

README = open('README').read()


def get_version():
    """ Copied from @nvie:

    https://github.com/nvie/rq/blob/master/setup.py
    I'm toooooo lazy ...
    """
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'gists/version.py')) as f:
        VERSION = None
        exec(f.read())
        return VERSION
    raise RuntimeError('No version info found.')

setup(
        name='gists',
        packages=['gists'],
        version=get_version(),
        author='Jaume Devesa',
        author_email='jaumedevesa@gmail.com',
        url='http://jdevesa.github.com/gists',
        description='CLI interface to manage Github gists',
        install_requires=['requests == 0.14.0', 'clint == 0.3.1'],
        scripts=['gists/gists'],
        include_package_data=True,
        long_description=README,
        license='MIT',
        test_suite='tests',
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Development Status :: 5 - Production/Stable ",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: POSIX :: Linux"
            ]
        )
