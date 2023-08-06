"""
Copyright 2012 Dian-Je Tsai and Wantoto Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from distutils.core import setup
from setuptools import find_packages
from eggplant import __version__ as eggplant_version

setup(
    name='django-eggplant',
    version=eggplant_version,
    author='sodas tsai',
    author_email='sodas@sodas.tw',
    packages=find_packages(exclude=('django_eggplant', 'eggplant_web')),
    url='https://bitbucket.org/sodastsai/django-eggplant/',
    license='Apache Software licence 2.0, see LICENCE.txt',
    description='Django base for common use',
    long_description=open('README.md').read(),
    keywords='django',
    zip_safe=False,
    include_package_data = True,
    install_requires = [
        'Django>=1.3',
        'Fabric>=1.5',
        'Jinja2>=2.6',
        'django-crispy-forms>=1.2',
        'django-fields>=0.2.0',
        'ground-soil>=0.1.13',
        'netaddr>=0.7',
        'python-dateutil>=2.1',
        'six>=1.2',
        'yajl>=0.3',
    ],
    classifiers=[
        'Framework :: Django',
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
