# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

setup(
    name="django-syncpermissions",
    packages=find_packages(),
    version="0.1.1",
    description="Sync permissions for specified apps, or all apps if none specified",
    author="RegioHelden GmbH",
    author_email="opensource@regiohelden.de",
    url="http://github.com/RegioHelden/django-syncpermissions",
    download_url='http://github.com/RegioHelden/django-syncpermissions',
    keywords=["django", "sync", "permissions"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
    install_requires=[
        "Django>=1.3",
    ],
    include_package_data=True,
    long_description=open("README.md").read(),
    zip_safe=False
)
