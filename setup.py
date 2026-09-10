# coding: utf-8
import os
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def read_version():
    """Single-source the version from pmdv/__init__.py without importing it."""
    init_py = os.path.join(here, 'pmdv', '__init__.py')
    with open(init_py, encoding='utf-8') as fh:
        match = re.search(r"""^__version__\s*=\s*['"]([^'"]+)['"]""", fh.read(), re.M)
    if not match:
        raise RuntimeError('Unable to find __version__ in pmdv/__init__.py')
    return match.group(1)


setup(
    name='pmdv',
    version=read_version(),
    author='DonghLee57',
    description='Portable Markdown Viewer with Live-Reload and Multi-Engine Swap',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DonghLee57/pmdv',
    project_urls={
        'Source': 'https://github.com/DonghLee57/pmdv',
        'Issue Tracker': 'https://github.com/DonghLee57/pmdv/issues',
    },
    license='MIT',
    packages=find_packages(exclude=['build', 'build.*', 'dist', 'dist.*']),
    install_requires=[],
    extras_require={
        'gui': ['pywebview>=6.0.0'],
    },
    entry_points={
        'console_scripts': [
            'pmdv=pmdv.viewer:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
)
