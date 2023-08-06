# -*- coding: utf-8 -*-
'''
Copyright 2012 Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from distutils.core import setup
from QSupervisorControl import VERSION

import os


def get_locales():
    i18n_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'QSupervisorControl',
        'data',
        'i18n'
    )
    locale_file = lambda x: os.path.join('data', 'i18n', x, 'LC_MESSAGES/*.mo')
    test = lambda x: os.path.isdir(os.path.join(i18n_dir, x))
    rst = [locale_file(filename) for filename in os.listdir(i18n_dir) if test(filename) is True]
    return rst

setup(
    name='QSupervisorControl',
    description='The simples tray system that observe status of services managed with supervisor.',
    long_description=open('README.rst', 'r').read(),
    version=VERSION,
    author='Rodrigo Pinheiro Matias',
    author_email='rodrigopmatias@gmail.com',
    maintainer='Rodrigo Pinheiro Matias',
    maintainer_email='rodrigopmatias@gmail.com',
    url='https://bitbucket.org/rodrigopmatias/qsupervisorcontrol/downloads',
    py_modules=['QSupervisorControl'],
    scripts=['QSupervisorControl.py'],
    install_requires=['supervisor', 'sqlalchemy'],
    packages=['QSupervisorControl', 'QSupervisorControl.ui', 'QSupervisorControl.ui.layout'],
    package_data={'QSupervisorControl': ['data/*.png'] + get_locales()}
)
