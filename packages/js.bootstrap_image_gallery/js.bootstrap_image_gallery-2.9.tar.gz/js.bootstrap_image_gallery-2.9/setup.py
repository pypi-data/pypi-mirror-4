import os

from setuptools import find_packages
from setuptools import setup

version = '2.9'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'bootstrap_image_gallery', 'test_bootstrap_image_gallery.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.bootstrap_image_gallery',
    version=version,
    description="Fanstatic packaging of Bootstrap Image Gallery",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'js.bootstrap',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'bootstrap_image_gallery = js.bootstrap_image_gallery:library',
            ],
        },
    )
