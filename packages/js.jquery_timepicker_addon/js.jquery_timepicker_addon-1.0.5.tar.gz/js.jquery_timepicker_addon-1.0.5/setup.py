from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.0.5'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_timepicker_addon', 'test_jquery-timepicker-addon.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_timepicker_addon',
    version=version,
    description="Fanstatic packaging of jQuery-Timepicker-Addon",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.jqueryui',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery-timepicker-addon = js.jquery_timepicker_addon:library',
            ],
        },
    )
