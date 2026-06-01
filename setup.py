# coding: utf-8
from setuptools import setup, find_packages

setup(
    name="pmdv",
    version="1.0.0",
    description="Portable Markdown Viewer with Live-Reload and Multi-Engine Swap",
    packages=find_packages(),
    install_requires=["pywebview>=6.0.0"],
    entry_points={
        'console_scripts': [
            'pmdv=pmdv.viewer:main',
        ],
    },
)
