from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-eggplant',
    version='0.1.3',
    author='sodas tsai',
    author_email='sodas@sodas.tw',
    packages=find_packages(exclude=('django_eggplant','eggplant_web')),
    #url='https://bitbucket.org/sodastsai/django-eggplant/',
    license='Apache Software licence 2.0, see LICENCE.txt',
    description='Django base for common use',
    long_description=open('README.md').read(),
    keywords='django',
    zip_safe=False,
    include_package_data = True,
    install_requires = [
        'django>=1.3',
        'django-crispy-forms>=1.2',
        'python-dateutil==2.1',
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