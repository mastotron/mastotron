from setuptools import setup
from setuptools import find_packages
pkgs=find_packages(exclude=('tests',))
with open('README.md') as f: readme=f.read()
with open('requirements.txt') as f: reqs=[x.strip() for x in f.read().split('\n') if x.strip()]

setup(
    name='mastotron',
    version='0.4.6',
    url=f"https://github.com/quadrismegistus/mastotron",
    license='MIT',
    author="Ryan Heuser",
    author_email="ryan.heuser@princeton.edu",
    description="Algorithmifying mastodon",
    long_description=readme,
    long_description_content_type="text/markdown",

    packages=pkgs,

    install_requires=reqs,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],


    py_modules=['mastotron'],
    entry_points={
        'console_scripts': [
            f'mastotron = mastotron.cli:cli',
        ],
    },
    package_data={
        '': ['static/*', 'templates/*'],
    }
)