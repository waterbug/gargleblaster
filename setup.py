#!/usr/bin/env python
"""
Setup script for Marvin.
"""
import os, site
from setuptools import setup, find_packages

VERSION = '4.4.dev0'

sitepkg_dir = [p for p in site.getsitepackages()
               if p.endswith('site-packages')][0]
doc_path = os.path.join('marvin', 'doc')
doc_file_paths = [os.path.join('doc', 'marvin_user_guide.html'),
                  os.path.join('doc', 'marvin_reference.html'),
                  os.path.join('doc', 'pandoc.css')]
doc_img_files = os.listdir(os.path.join('doc', 'images'))
doc_img_paths = [os.path.join('doc', 'images', p)
                 for p in doc_img_files]
data_mod_path = os.path.join('marvin', 'test', 'data')
data_paths = [os.path.join(data_mod_path, p)
               for p in os.listdir(data_mod_path)
               if not p.startswith('__init__')]

setup(
    name="marvin",
    version=VERSION,
    description="Collaborative Assistive Tool To Enable Novel Solutions",
    author="Stephen Waterbury",
    author_email="stephen.c.waterbury@nasa.gov",
    install_requires=[
        'pangalactic.node>=4.4.dev0'
        ],
    keywords='',
    maintainer="Stephen Waterbury",
    maintainer_email="stephen.c.waterbury@nasa.gov",
    url="",
    license="NASA",
    long_description=(
      "A desktop GUI client for collaborative Model-Based Engineering (MBE)."),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'marvin = marvin.__main__:main',
        ],
        'gui_scripts': [
            'marvin = marvin.__main__:main',
        ]
    },
    data_files=[
        # doc files (user guide)
        (os.path.join(sitepkg_dir, doc_path), doc_file_paths),
        # doc image files
        (os.path.join(sitepkg_dir, doc_path, 'images'), doc_img_paths),
        # data files
        (os.path.join(sitepkg_dir, data_mod_path), data_paths),
        ]
    )

