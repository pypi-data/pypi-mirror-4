import os

from setuptools import find_packages
from setuptools import setup

name = 'deform_widget_dynatree'
version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name=name,
    version=version,
    description="jQuery dynatree widget for deform",
    long_description=README + '\n\n' + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Pylons',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Widget Sets',
    ],
    keywords='deform widget',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/disko/deform_widget_dynatree',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "deform"
    ],
    entry_points={},
)
