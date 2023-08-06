# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.1.1'
long_description = '\n'.join([
        open(os.path.join("src", "README.txt")).read(),
        open(os.path.join("src", "AUTHORS.txt")).read(),
        open(os.path.join("src", "HISTORY.txt")).read(),
        ])

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

setup(
    name='sphinxjp.themes.trstyle',
    version=version,
    description='A sphinx theme for TriAx Corp style Documentation.',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['sphinx', 'reStructuredText', 'theme'],
    author='TriAx Corp',
    author_email='junichi dot kakisako at triax dot jp',
    url='https://bitbucket.org/kironono/sphinxjp.themes.trstyle',
    license='MIT',
    namespace_packages=['sphinxjp', 'sphinxjp.themes'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[
        'setuptools',
        'docutils',
        'sphinx',
        'sphinxjp.themecore',
    ],
    entry_points="""
        [sphinx_themes]
        path = sphinxjp.themes.trstyle:template_path

        [sphinx_directives]
        setup = sphinxjp.themes.trstyle:setup
    """,
    zip_safe=False,
)

