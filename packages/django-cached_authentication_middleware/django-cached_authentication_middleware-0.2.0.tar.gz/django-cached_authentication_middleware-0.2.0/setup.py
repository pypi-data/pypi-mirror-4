# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-cached_authentication_middleware',
    version='0.2.0',
    author='Selwin Ong',
    author_email='selwin.ong@gmail.com',
    packages=['cached_auth'],
    url='https://github.com/ui/django-cached_authentication_middleware',
    license='MIT',
    description="A drop in replacement for django's built in AuthenticationMiddleware that utilizes caching.",
    long_description=open('README.rst').read(),
    zip_safe=False,
    include_package_data=True,
    package_data = { '': ['README.rst'] },
    install_requires=['django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
