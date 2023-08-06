import os
from setuptools import find_packages
from setuptools import setup

version = '0.4.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'angular_ui', 'test_angularui.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.angular_ui',
    version=version,
    description="Fanstatic packaging of AngularUI",
    long_description=long_description,
    classifiers=[],
    keywords='',
    license='MIT',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.angular',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'angularui = js.angular_ui:library',
        ],
    },
)
