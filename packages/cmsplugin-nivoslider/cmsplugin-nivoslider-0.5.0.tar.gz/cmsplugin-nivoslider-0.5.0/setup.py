# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='cmsplugin-nivoslider',
    version='0.5.0',
    author='Bernardo Cabezas Serra, Bertrand Bordage, Marion Balensi',
    author_email='bcabezas@apsl.net',
    packages = find_packages(),
    license='MIT',
    description = "Simple Nivo Slider plugin for django-cms",
    long_description=open('README.rst').read(),
    install_requires=['django-cms', 'django-filer',],
    url='https://bitbucket.org/bercab/cmsplugin-nivoslider',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    include_package_data=True,
    zip_safe=False,
)
