import mastotron as pkg
from setuptools import setup
with open('README.md') as f: readme=f.read()
with open('requirements.txt') as f: reqs=[x.strip() for x in f.read().split('\n') if x.strip()]

setup(
    name=pkg.__name__,
    version=pkg.__version__,
    py_modules=[pkg.__name__],
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            f'{pkg.__name__} = cli:cli',
        ],
    },
    include_package_data=True
)