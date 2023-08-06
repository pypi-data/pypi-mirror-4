#!/usr/bin/env python
from distutils.core import setup

version='0.4.1'

setup(
    name='django-vkontakte-iframe',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['vk_iframe', 'vk_iframe.migrations'],
    package_data={
        'vk_iframe': ['templates/vk_iframe/default/403.html', 'fixtures/vk-geo.json']
    },

    url='https://bitbucket.org/kmike/django-vkontakte-iframe/',
    license='MIT license',
    description="Django app for developing vk.com (aka vkontakte.ru) iframe applications",

    long_description = open('README.rst').read() + "\n\n"+ open('CHANGES.rst').read(),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
