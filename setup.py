# coding: utf-8
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pmdv',
    version='1.0.0',
    author='DonghLee57',
    description='Portable Markdown Viewer with Live-Reload and Multi-Engine Swap',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DonghLee57/pmdv',
    packages=find_packages(),
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
    ],
    python_requires='>=3.7',
)
