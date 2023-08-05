from setuptools import setup, find_packages
import os

version = '2.9.3'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'mediaelement', 'test_mediaelement.js.txt')
    + '\n' +
    read('CHANGES.txt')
)

setup(
    name='js.mediaelement',
    version=version,
    description="Fanstatic packaging of MediaElement.js",
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
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'mediaelement.js = js.mediaelement:library',
        ],
    },
)
